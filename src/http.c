#ifndef HTTP_H
#define HTTP_H

#include <stddef.h>

/**
 * parse_http_request
 * ------------------
 * Parse la première ligne d'une requête HTTP et extrait :
 *   - method : "GET", "POST", ...
 *   - path   : "/hello", "/stats", ...
 *   - query  : partie après '?' (ex: "a=1&b=2"), sinon chaîne vide.
 *
 * Les buffers method, path, query doivent être préalloués par l'appelant.
 * En cas d'erreur de parsing, on renvoie des valeurs par défaut sûres :
 *   method = "GET", path = "/", query = "".
 *
 * @param raw         Buffer brut contenant la requête HTTP.
 * @param method_out  Buffer de sortie pour la méthode (ex: char[16]).
 * @param path_out    Buffer de sortie pour le chemin (ex: char[256]).
 * @param query_out   Buffer de sortie pour la query (ex: char[256]).
 */
void parse_http_request(const char *raw,
                        char *method_out,
                        char *path_out,
                        char *query_out);

/**
 * send_http_response
 * ------------------
 * Envoie une réponse HTTP/1.1 complète sur le socket client_fd.
 *
 * Génère automatiquement :
 *   - Status line      : HTTP/1.1 <status>\r\n
 *   - Date             : Date: <GMT>\r\n
 *   - Server           : Server: server_project/1.0\r\n
 *   - Content-Type     : <content_type>; charset=utf-8\r\n
 *   - Content-Length   : <len(body)>\r\n
 *   - Connection       : <connection>\r\n
 *   - Ligne vide       : \r\n
 *   - Corps            : body
 *
 * @param client_fd     Descripteur de socket.
 * @param status        Ex: "200 OK", "404 Not Found".
 * @param content_type  Ex: "text/html", "application/json".
 * @param body          Corps de la réponse (peut être NULL => vide).
 * @param connection    "close" ou "keep-alive" (NULL => "close").
 *
 * @return 0 en cas de succès, -1 en cas d'erreur d'envoi.
 */
int send_http_response(int client_fd,
                       const char *status,
                       const char *content_type,
                       const char *body,
                       const char *connection);

#endif /* HTTP_H */