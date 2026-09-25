# -*- coding: utf-8 -*-
"""Cliente XML-RPC para Kiwi TCMS.

Copiado sin modificar de C:\\IA\\kiwi-tcms\\rpc_client.py, el patrón ya
verificado en whatsapp-mcp e ia-evaluator. No se toca desde tokmd.
"""
import http.client
import ssl
import xmlrpc.client


class CookieTransport(xmlrpc.client.SafeTransport):
    def __init__(self, context):
        super().__init__(context=context)
        self._cookie = None

    def send_headers(self, connection, headers):
        if self._cookie:
            connection.putheader("Cookie", self._cookie)
        super().send_headers(connection, headers)

    def parse_response(self, response):
        cookies = response.msg.get_all("Set-Cookie") or []
        crumbs = [c.split(";")[0] for c in cookies]
        if crumbs:
            self._cookie = "; ".join(crumbs)
        return super().parse_response(response)


def connect(host="127.0.0.1", port=8443, username=None, password=None):
    ctx = ssl._create_unverified_context()
    transport = CookieTransport(context=ctx)
    url = f"https://{host}:{port}/xml-rpc/"
    rpc = xmlrpc.client.ServerProxy(url, transport=transport, allow_none=True)
    if username:
        rpc.Auth.login(username, password)
    return rpc
