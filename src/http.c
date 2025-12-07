
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include "http.h"

void parse_http_request(const char *req, char *method, char *path, char *query) {
    char line[1024] = {0};

    /* extraire la première ligne */
    const char *end = strstr(req, "\r\n");
    if (end) {
        size_t len = end - req;
        if (len > 1023) len = 1023;
        memcpy(line, req, len);
        line[len] = '\0';
    } else {
        strncpy(line, req, sizeof(line) - 1);
    }

    char raw_path[512] = {0};
    sscanf(line, "%s %s", method, raw_path);

    char *q = strchr(raw_path, '?');
    if (q) {
        strcpy(query, q + 1);
        *q = '\0';
    } else {
        query[0] = '\0';
    }

    strcpy(path, raw_path);
}

void send_http_response(int client_fd,
                        const char *status,
                        const char *content_type,
                        const char *body) {

    char header[2048];
    int content_length = strlen(body);

    int n = snprintf(header, sizeof(header),
        "HTTP/1.1 %s\r\n"
        "Content-Type: %s\r\n"
        "Content-Length: %d\r\n"
        "Connection: close\r\n\r\n",
        status, content_type, content_length
    );

    send(client_fd, header, n, 0);
    send(client_fd, body, content_length, 0);
}
