import type { NextConfig } from "next";

const config: NextConfig = {
  async rewrites() {
    // Server-only setting: never send database credentials or this origin to the browser.
    const origin = process.env.API_ORIGIN || "http://127.0.0.1:8000";
    return [{ source: "/api/v1/:path*", destination: origin + "/api/v1/:path*" }];
  },
};
export default config;
