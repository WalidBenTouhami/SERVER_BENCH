#include "../src/http.h"
#include <assert.h>
#include <string.h>
#include <stdio.h>

void test_parse_simple() {
    http_request_t req;

    const char *raw =
        "GET /hello?name=walid HTTP/1.1\r\n"
        "Host: localhost\r\n"
        "\r\n";

    assert(parse_http_request(raw, &req) == 0);
    assert(strcmp(req.method, "GET") == 0);
    assert(strcmp(req.path, "/hello") == 0);
    assert(strcmp(req.query, "name=walid") == 0);
}

void test_parse_no_query() {
    http_request_t req;

    const char *raw = "POST /api HTTP/1.1\r\n\r\n";

    assert(parse_http_request(raw, &req) == 0);
    assert(strcmp(req.method, "POST") == 0);
    assert(strcmp(req.path, "/api") == 0);
    assert(strcmp(req.query, "") == 0);
}

int main() {
    printf("Running HTTP tests…\n");

    test_parse_simple();
    test_parse_no_query();

    printf("All HTTP tests passed successfully.\n");
    return 0;
}