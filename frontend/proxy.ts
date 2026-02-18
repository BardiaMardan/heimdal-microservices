import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const publicRoutes = ["/login", "/signup", "/"];

export function proxy(request: NextRequest) {
  const token = request.cookies.get("session")?.value;
  const isPublicRoute = publicRoutes.includes(request.nextUrl.pathname);

  if (!token && !isPublicRoute) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  if (token && isPublicRoute) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
