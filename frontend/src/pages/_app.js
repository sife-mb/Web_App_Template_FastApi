import { SessionProvider } from "next-auth/react";
import '@/styles/globals.css';

// Diese Datei ist die "Haupt-Schale" der Next.js-Anwendung

function MyApp({ Component, pageProps: { session, ...pageProps } }) {
  return (
    // Der SessionProvider stellt die Login-Informationen (die "Session")
    // allen Unter-Komponenten zur Verfügung.
    <SessionProvider session={session}>
      <Component {...pageProps} />
    </SessionProvider>
  );
}

export default MyApp;



