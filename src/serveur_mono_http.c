#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#include <unistd.h>
#include "http.h"

#define PORT 5050

int main() {
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);

    struct sockaddr_in addr = {0};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(PORT);
    addr.sin_addr.s_addr = INADDR_ANY;

    bind(server_fd, (struct sockaddr*)&addr, sizeof(addr));
    listen(server_fd, 10);

    printf("Serveur HTTP mono-thread sur port %d...\n", PORT);

    char buffer[4096];

    while (1) {
        int client_fd = accept(server_fd, NULL, NULL);
        int n = recv(client_fd, buffer, sizeof(buffer)-1, 0);
        if (n <= 0) { close(client_fd); continue; }

        buffer[n] = '\0';

        char method[16], path[256], query[256];
        parse_http_request(buffer, method, path, query);

        printf("→ METHOD=%s | PATH=%s\n", method, path);

        if (strcmp(path, "/hello") == 0) {
            send_http_response(client_fd, "application/json",
                "{\"msg\":\"Bonjour depuis mono-thread\"}");
        } else {
            send_http_response(client_fd, "text/plain", "404 NOT FOUND");
        }
        close(client_fd);
    }
    return 0;
}
