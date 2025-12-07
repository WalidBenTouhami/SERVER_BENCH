
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include "http.h"

#define HTTP_PORT 8080
#define BACKLOG   32

int main(void) {
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) { perror("socket"); exit(1); }

    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in addr = {0};
    addr.sin_family      = AF_INET;
    addr.sin_port        = htons(HTTP_PORT);
    addr.sin_addr.s_addr = INADDR_ANY;

    if (bind(server_fd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        perror("bind"); exit(1);
    }
    if (listen(server_fd, BACKLOG) < 0) {
        perror("listen"); exit(1);
    }

    printf("[HTTP-MONO] Serveur HTTP mono-thread sur port %d\n", HTTP_PORT);

    for (;;) {
        int client = accept(server_fd, NULL, NULL);
        if (client < 0) { perror("accept"); continue; }

        char buffer[4096];
        ssize_t n = recv(client, buffer, sizeof(buffer) - 1, 0);
        if (n <= 0) { close(client); continue; }

        buffer[n] = '\0';

        char method[16] = {0};
        char path[256]  = {0};
        char query[256] = {0};

        parse_http_request(buffer, method, path, query);
        printf("[MONO_HTTP] METHOD='%s' | PATH='%s'\n", method, path);

        if (strcmp(path, "/hello") == 0) {
            send_http_response(client,
                               "200 OK",
                               "application/json",
                               "{\"msg\":\"Bonjour depuis serveur mono-thread\"}");
        } else {
            send_http_response(client,
                               "404 Not Found",
                               "text/plain",
                               "404 NOT FOUND");
        }

        close(client);
    }

    return 0;
}
