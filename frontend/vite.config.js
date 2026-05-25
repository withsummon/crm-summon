import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import path from 'path'
import { VitePWA } from 'vite-plugin-pwa'

// https://vitejs.dev/config/
export default defineConfig(async ({ mode }) => {
  const isDev = mode === 'development'
  const backendHost = process.env.FRAPPE_DEV_SITE || 'crm.localhost'
  const backendPort = Number(process.env.FRAPPE_WEB_SERVER_PORT || 8000)
  const devServerPort = Number(process.env.CRM_DEV_SERVER_PORT || 8080)
  const backendTarget = `http://127.0.0.1:${backendPort}`
  const backendProxy = {
    target: backendTarget,
    ws: true,
    changeOrigin: false,
    headers: {
      Host: backendHost,
    },
    cookieDomainRewrite: '', // Removes domain attribute so it binds to the actual browser host (localhost or crm.localhost)
    configure: (proxy, options) => {
      proxy.on('proxyRes', (proxyRes, req, res) => {
        if (proxyRes.headers.location) {
          try {
            let location = proxyRes.headers.location
            if (location.startsWith('http://') || location.startsWith('https://')) {
              const url = new URL(location)
              if (url.hostname === 'crm.localhost' || url.hostname === '127.0.0.1') {
                url.host = req.headers.host
                proxyRes.headers.location = url.toString()
              }
            }
          } catch (e) {
            console.error('Failed to rewrite location header:', e)
          }
        }
        // Strip Secure flag from cookies in local dev (HTTP)
        const cookies = proxyRes.headers['set-cookie']
        if (cookies) {
          proxyRes.headers['set-cookie'] = cookies.map((cookie) =>
            cookie.replace(/;\s*Secure/i, ''),
          )
        }
      })
    },
  }
  const backendRootPostProxy = {
    ...backendProxy,
    bypass: (req) => {
      if (req.method !== 'POST') {
        return req.url
      }
    },
  }

  const config = {
    plugins: [
      vue(),
      vueJsx(),
      VitePWA({
        registerType: 'autoUpdate',
        devOptions: {
          enabled: true,
        },
        manifest: {
          display: 'standalone',
          name: 'BNI CRM',
          short_name: 'BNI CRM',
          start_url: '/crm',
          description:
            'BNI teal CRM workspace for lead generation and customer 360',
          icons: [
            {
              src: '/assets/crm/images/bni-logo.png',
              sizes: '192x192',
              type: 'image/png',
              purpose: 'any',
            },
            {
              src: '/assets/crm/images/bni-logo.png',
              sizes: '192x192',
              type: 'image/png',
              purpose: 'maskable',
            },
            {
              src: '/assets/crm/images/bni-logo.png',
              sizes: '512x512',
              type: 'image/png',
              purpose: 'any',
            },
            {
              src: '/assets/crm/images/bni-logo.png',
              sizes: '512x512',
              type: 'image/png',
              purpose: 'maskable',
            },
          ],
        },
      }),
    ],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
        'vuex': path.resolve(__dirname, 'src/modules/drive/store.js'),
      },
    },
    optimizeDeps: {
      include: [
        'feather-icons',
        'tailwind.config.js',
        'prosemirror-state',
        'prosemirror-view',
        'lowlight',
        'interactjs',
      ],
    },
    server: {
      host: '0.0.0.0',
      port: devServerPort,
      strictPort: true,
      allowedHosts: [
        '.ngrok-free.app',
        '.ngrok-free.dev',
        '.share.zrok.io',
      ],
      fs: {
        allow: [path.resolve(__dirname, '..')],
      },
      proxy: {
        '^/$': backendRootPostProxy,
        '/api': backendProxy,
        '/app': backendProxy,
        '/assets': backendProxy,
        '/desk': backendProxy,
        '/drive': backendProxy,
        '/files': backendProxy,
        '/helpdesk': backendProxy,
        '/insights': backendProxy,
        '/login': backendProxy,
        '/private': backendProxy,
        '/website_script.js': backendProxy,
        '/favicon.ico': backendProxy,
        '/robots.txt': backendProxy,
      },
    },
  }

  const frappeui = await importFrappeUIPlugin(isDev, config)
  config.plugins.unshift(
    frappeui({
      frappeProxy: false,
      lucideIcons: true,
      jinjaBootData: true,
      buildConfig: {
        indexHtmlPath: '../crm/www/crm.html',
        emptyOutDir: true,
        sourcemap: true,
      },
    }),
  )

  return config
})

async function importFrappeUIPlugin(isDev, config) {
  if (isDev) {
    try {
      // Check if local frappe-ui has the vite plugin file
      const fs = await import('node:fs')
      const localVitePluginPath = path.resolve(__dirname, '../frappe-ui/vite')

      if (fs.existsSync(localVitePluginPath)) {
        const module = await import('../frappe-ui/vite')
        console.info('Local frappe-ui vite plugin found, using local plugin')
        config.resolve.alias = getAliases(config)
        return module.default
      } else {
        console.warn('Local frappe-ui vite plugin not found, using npm package')
      }
    } catch (error) {
      console.warn(
        'Local frappe-ui not found, falling back to npm package:',
        error.message,
      )
    }
  }
  // Fall back to npm package if local import fails
  const module = await import('frappe-ui/vite')
  return module.default
}

function getAliases(config) {
  return {
    ...config.resolve.alias,
    'frappe-ui/tailwind': path.resolve(
      __dirname,
      '../frappe-ui/tailwind/preset.js',
    ),
    'frappe-ui/style.css': path.resolve(
      __dirname,
      '../frappe-ui/src/style.css',
    ),
    'frappe-ui/frappe': path.resolve(__dirname, '../frappe-ui/frappe/index.js'),
    'frappe-ui': path.resolve(__dirname, '../frappe-ui/src/index.ts'),
  }
}
