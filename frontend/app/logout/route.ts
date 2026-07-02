import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

// Route Handler (not a Server Action) so we can legally delete the cookie
// during a redirect. fetchApi() redirects here on any 401 so an invalid or
// expired token is cleared instead of ping-ponging /dashboard <-> /login.
export async function GET(request: NextRequest) {
  const cookieStore = await cookies();
  cookieStore.delete("session");
  return NextResponse.redirect(new URL("/login", request.url));
}
