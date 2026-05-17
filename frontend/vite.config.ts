import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"
import path from "path"

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (p) => {
          const stripped = p.replace(/^\/api/, "")
          const [path, qs] = stripped.split("?")
          const withSlash = path.endsWith("/") ? path : path + "/"
          return qs ? withSlash + "?" + qs : withSlash
        },
      },
    },
  },
})
