import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Script from "next/script";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "QKraft - AI Driven Schema & Query Optimizer",
  description: "Direct schema auto-optimization, SQL relational diagrams, and database query performance benchmarking.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning className={`${geistSans.variable} ${geistMono.variable}`}>
      <head>
        <Script
          id="suppress-extension-errors"
          strategy="beforeInteractive"
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                if (typeof window === 'undefined') return;
                function isExtensionError(err, event) {
                  var str = (err && (err.stack || err.message)) || (event && (event.filename || event.message)) || '';
                  return typeof str === 'string' && (
                    str.indexOf('chrome-extension:') !== -1 || 
                    str.indexOf('moz-extension:') !== -1 || 
                    str.indexOf('safari-web-extension:') !== -1 ||
                    str.indexOf('embed_script.js') !== -1
                  );
                }
                var origError = console.error;
                console.error = function() {
                  var str = Array.prototype.slice.call(arguments).map(function(a) { 
                    return (a && a.stack) ? a.stack : String(a || ''); 
                  }).join(' ');
                  if (str.indexOf('chrome-extension:') !== -1 || str.indexOf('embed_script.js') !== -1) {
                    return;
                  }
                  return origError.apply(console, arguments);
                };
                window.addEventListener('error', function(e) {
                  if (isExtensionError(e.error, e)) {
                    e.stopImmediatePropagation();
                    e.preventDefault();
                    return true;
                  }
                }, true);
                window.addEventListener('unhandledrejection', function(e) {
                  if (isExtensionError(e.reason, e)) {
                    e.stopImmediatePropagation();
                    e.preventDefault();
                  }
                }, true);
              })();
            `,
          }}
        />
      </head>
      <body suppressHydrationWarning>{children}</body>
    </html>
  );
}

