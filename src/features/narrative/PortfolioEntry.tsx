import Image from "next/image";
import Link from "next/link";

export default function PortfolioEntry() {
  return (
    <main className="portfolio-entry">
      <nav aria-label="Portfolio" className="portfolio-nav">
        <Link className="portfolio-brand" href="/" aria-label="Yoreny home">
          <span className="portfolio-mark">
            <Image src="/brand/yoreny-mark-burgundy-v1.png" alt="" width={42} height={42} priority />
          </span>
          <span className="portfolio-wordmark">yoreny</span>
        </Link>
        <span>Portfolio / CV</span>
      </nav>
      <section className="portfolio-intro">
        <p className="portfolio-kicker">RESEARCH · DATA · INTERACTION</p>
        <h1>Personal portfolio</h1>
        <p>This route is reserved for the personal CV and portfolio. Melbourne Urban Pulse is presented as one inspectable research project within it.</p>
        <Link className="portfolio-project" href="/projects/melbourne-urban-pulse">
          <span>Featured research project</span>
          <strong>Melbourne Urban Pulse</strong>
          <span>Open project narrative →</span>
        </Link>
      </section>
    </main>
  );
}
