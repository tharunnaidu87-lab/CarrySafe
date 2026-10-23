import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwind from "@tailwindcss/vite";
export default defineConfig({
  plugins: [react(), tailwind()],
  server: {
    allowedHosts: ["terminal.local"],
    proxy: { "/api": "http://127.0.0.1:8000", "/mcp": "http://127.0.0.1:8000" },
  },
});
