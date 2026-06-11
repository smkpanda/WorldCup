import { NextRequest, NextResponse } from "next/server";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  if (pathname === "/") return NextResponse.redirect(new URL("/en", request.url));
  if (/^\/(review|methodology|matches)(\/|$)/.test(pathname)) {
    return NextResponse.redirect(new URL(`/en${pathname}`, request.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/", "/review/:path*", "/methodology/:path*", "/matches/:path*"],
};
