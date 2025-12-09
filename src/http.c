#include "http.h"

#include <stdio.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/socket.h>

/* --------------------------------------------------------------------------
 * Helpers internes
 * -------------------------------------------------------------------------- */

/* Trim en place (espaces/tabs en début/fin) */
static void trim_spaces(char *s) {
    if (!s || !*s) return;

    char *start = s;
    while (*start == ' ' || *start == '\t' || *start == '\r' || *start == '\n')
        start++;

    char *end = start + strlen(start);
    while (end > start &&
           (end[-1] == ' ' || end[-1] == '\t' || end[-1] == '\r' || end[-1] == '\n'))
    {
        end--;
    }
    *end = '\0';

    if (start != s)
        memmove(s, start, end - start + 1);
}

/* Copie sécurisée avec terminaison */
static void safe_copy(char *dest, size_t dest_size,
                      const char *src, size_t src_len)
{
    if (!dest || dest_size == 0) return;
    if (!src) {
        dest[0] = '\0';
        return;
    }
    if (src_len >= dest_size)
        src_len = dest_size - 1;
    memcpy(dest, src, src_len);
    dest[src_len] = '\0';
}

/* --------------------------------------------------------------------------
 * Parser HTTP — première ligne "METHOD SP REQUEST_TARGET SP HTTP/VERSION"
 * -------------------------------------------------------------------------- */
void parse_http_request(const char *raw,
                        char *method_out,
                        char *path_out,
                        char *query_out)
{
    /* Valeurs par défaut sûres */
    if (method_out) method_out[0] = '\0';
    if (path_out)   path_out[0]   = '\0';
    if (query_out)  query_out[0]  = '\0';

    if (!raw || !method_out || !path_out || !query_out) {
        /* Defaults */
        if (method_out) strcpy(method_out, "GET");
        if (path_out)   strcpy(path_out, "/");
        if (query_out)  query_out[0] = '\0';
        return;
    }

    /* On récupère la première ligne jusqu'à \r\n ou \n */
    const char *line_end = strstr(raw, "\r\n");
    if (!line_end) {
        line_end = strchr(raw, '\n');
    }

    size_t line_len;
    if (line_end)
        line_len = (size_t)(line_end - raw);
    else
        line_len = strlen(raw);  /* Repli : tout le buffer */

    char line[1024];
    if (line_len >= sizeof(line))
        line_len = sizeof(line) - 1;
    memcpy(line, raw, line_len);
    line[line_len] = '\0';

    /* Trim de sécurité */
    trim_spaces(line);

    if (line[0] == '\0') {
        /* Ligne vide => requête invalide, valeurs par défaut */
        strcpy(method_out, "GET");
        strcpy(path_out, "/");
        query_out[0] = '\0';
        return;
    }

    /* Tokenisation : METHOD SP REQUEST_TARGET SP HTTP/VERSION */
    const char *p = line;

    /* METHOD */
    while (*p == ' ' || *p == '\t')
        p++;
    const char *method_start = p;
    while (*p && *p != ' ' && *p != '\t')
        p++;
    size_t method_len = (size_t)(p - method_start);
    if (method_len == 0) {
        strcpy(method_out, "GET");
        strcpy(path_out, "/");
        query_out[0] = '\0';
        return;
    }
    safe_copy(method_out, 16, method_start, method_len); /* method[16] côté appelant */

    /* REQUEST_TARGET */
    while (*p == ' ' || *p == '\t')
        p++;
    const char *target_start = p;
    while (*p && *p != ' ' && *p != '\t')
        p++;
    size_t target_len = (size_t)(p - target_start);
    if (target_len == 0) {
        strcpy(path_out, "/");
        query_out[0] = '\0';
        return;
    }

    /* Split path + query sur '?' */
    const char *qmark = memchr(target_start, '?', target_len);
    if (!qmark) {
        /* Pas de query */
        safe_copy(path_out, 256, target_start, target_len); /* path[256] côté appelant */
        query_out[0] = '\0';
    } else {
        size_t path_len = (size_t)(qmark - target_start);
        size_t query_len = (size_t)((target_start + target_len) - (qmark + 1));
        safe_copy(path_out, 256, target_start, path_len);
        safe_copy(query_out, 256, qmark + 1, query_len);
    }

    /* En cas de path vide => "/" */
    if (path_out[0] == '\0') {
        strcpy(path_out, "/");
    }
}

/* --------------------------------------------------------------------------
 * Envoi de réponse HTTP
 * -------------------------------------------------------------------------- */
int send_http_response(int client_fd,
                       const char *status,
                       const char *content_type,
                       const char *body,
                       const char *connection)
{
    if (client_fd < 0) {
        return -1;
    }

    if (!status) {
        status = "200 OK";
    }
    if (!content_type) {
        content_type = "text/plain";
    }
    if (!body) {
        body = "";
    }
    if (!connection) {
        connection = "close";
    }

    size_t body_len = strlen(body);

    /* Date HTTP en GMT */
    char date_buf[128];
    {
        time_t now = time(NULL);
        struct tm tm_now;
#if defined(_POSIX_THREAD_SAFE_FUNCTIONS) && !defined(__APPLE__)
        gmtime_r(&now, &tm_now);
#else
        struct tm *tmp = gmtime(&now);
        if (tmp) tm_now = *tmp;
#endif
        strftime(date_buf, sizeof(date_buf),
                 "%a, %d %b %Y %H:%M:%S GMT", &tm_now);
    }

    char header[1024];
    int n = snprintf(header, sizeof(header),
                     "HTTP/1.1 %s\r\n"
                     "Date: %s\r\n"
                     "Server: server_project/1.0\r\n"
                     "Content-Type: %s; charset=utf-8\r\n"
                     "Content-Length: %zu\r\n"
                     "Connection: %s\r\n"
                     "\r\n",
                     status,
                     date_buf,
                     content_type,
                     body_len,
                     connection);
    if (n <= 0) {
        return -1;
    }
    size_t header_len = (size_t)n;
    if (header_len > sizeof(header))
        header_len = sizeof(header);

    /* Envoi header */
    ssize_t sent = send(client_fd, header, header_len, 0);
    if (sent < 0) {
        return -1;
    }

    /* Envoi corps (si non vide) */
    if (body_len > 0) {
        ssize_t sent_body = send(client_fd, body, body_len, 0);
        if (sent_body < 0) {
            return -1;
        }
    }

    return 0;
}