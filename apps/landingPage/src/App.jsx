import { useMemo, useState } from "react";
import copy from "./content.json";
import { motion } from "framer-motion";
import {
  CheckCircle2,
  Sparkles,
  PlayCircle,
  ArrowRight,
  Star,
  BookOpen,
  Headphones,
  BarChart3,
  ShieldCheck,
  HelpCircle,
} from "lucide-react";

// --- Utility ---
const cx = (...cls) => cls.filter(Boolean).join(" ");
const fade = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0 },
};

// Badge component
const Badge = ({ children }) => (
  <span className="inline-flex items-center gap-1 rounded-full bg-gray-100 px-3 py-1 text-xs text-black ring-1 ring-gray-300">
    <Sparkles size={14} /> {children}
  </span>
);

// Section wrapper
const Section = ({ id, eyebrow, title, subtitle, children }) => (
  <section id={id} className="py-16 md:py-24">
    <div className="mx-auto max-w-6xl px-4">
      {eyebrow && (
        <div className="mb-3 text-xs font-medium uppercase tracking-wider text-red-500">
          {eyebrow}
        </div>
      )}
      {title && (
        <h2 className="text-2xl md:text-4xl font-bold text-black">
          {title}
        </h2>
      )}
      {subtitle && (
        <p className="mt-3 max-w-3xl text-gray-600">{subtitle}</p>
      )}
      <div className="mt-8">{children}</div>
    </div>
  </section>
);

// Accordion (FAQ)
const AccordionItem = ({ q, a }) => {
  const [open, setOpen] = useState(false);
  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-4">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between text-left"
      >
        <span className="text-black font-medium">{q}</span>
        <HelpCircle className={cx("ml-4 transition", open && "rotate-45")} />
      </button>
      <div
        className={cx(
          "grid transition-[grid-template-rows] duration-300 ease-in-out",
          open ? "grid-rows-[1fr]" : "grid-rows-[0fr]"
        )}
      >
        <div className="overflow-hidden">
          <p className="mt-3 text-gray-600 leading-relaxed">{a}</p>
        </div>
      </div>
    </div>
  );
};

// Comparison Table
const ComparisonTable = ({ rows }) => (
  <div className="overflow-x-auto rounded-2xl border border-gray-200 bg-white">
    <table className="min-w-full text-sm">
      <thead>
        <tr className="bg-gray-50 text-gray-600">
          <th className="px-4 py-3 text-left">{copy.comparison.title}</th>
          <th className="px-4 py-3 text-left">책</th>
          <th className="px-4 py-3 text-left">학원</th>
          <th className="px-4 py-3 text-left">튜터링</th>
          <th className="px-4 py-3 text-left">기존 앱</th>
          <th className="px-4 py-3 text-left">우리</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((r, i) => (
          <tr key={i} className="border-t border-gray-200">
            <td className="px-4 py-4 font-medium text-black">{r.criteria}</td>
            <td className="px-4 py-4 text-gray-600">{r.book}</td>
            <td className="px-4 py-4 text-gray-600">{r.academy}</td>
            <td className="px-4 py-4 text-gray-600">{r.tutoring}</td>
            <td className="px-4 py-4 text-gray-600">{r.app}</td>
            <td className="px-4 py-4 text-red-500">{r.ours}</td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

// Price Card
const PriceCard = ({ plan }) => (
  <div className="rounded-3xl border border-gray-200 bg-white p-6 backdrop-blur-sm shadow-xl">
    <div className="flex items-center gap-2">
      <Star className="text-red-500" size={18} />
      <h4 className="text-lg font-semibold text-black">{plan.name}</h4>
    </div>
    <div className="mt-2 text-3xl font-bold text-black">{plan.price_krw}</div>
    <p className="mt-1 text-gray-600">{plan.desc}</p>
    <ul className="mt-4 space-y-2">
      {plan.includes.map((it, idx) => (
        <li key={idx} className="flex items-start gap-2 text-gray-600">
          <CheckCircle2 className="mt-0.5 text-red-500" size={18} />
          <span>{it}</span>
        </li>
      ))}
    </ul>
    <button className="mt-6 w-full rounded-xl bg-red-500 px-4 py-3 font-semibold text-white shadow-lg shadow-red-500/20 hover:bg-red-400">
      {plan.cta}
    </button>
  </div>
);

// Metrics pill
const Metric = ({ text }) => (
  <div className="rounded-2xl bg-gray-100 px-4 py-3 text-sm text-black ring-1 ring-gray-300">
    {text}
  </div>
);

function App() {
  const c = copy; // alias
  const heroHeadline = useMemo(
    () => c.hero.headline || c.hero.headline_variants?.[0],
    [c]
  );

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-100 via-white to-gray-200 selection:bg-red-400/40">
      {/* NAV */}
      <header className="sticky top-0 z-40 border-b border-gray-300 bg-white/90 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
          <div className="flex items-center gap-2">
            <img src="/onigiri.jpg" alt="Onigiri" className="w-8 h-8 rounded-full" />
            <span className="text-black font-semibold">
              {c.brand.name_ko}
            </span>
          </div>
          <nav className="hidden gap-6 text-sm text-gray-600 md:flex">
            <a href="#features" className="hover:text-black">
              기능
            </a>
            <a href="#how" className="hover:text-black">
              사용법
            </a>
            <a href="#reviews" className="hover:text-black">
              후기
            </a>
            <a href="#comparison" className="hover:text-black">
              비교표
            </a>
            <a href="#faq" className="hover:text-black">
              FAQ
            </a>
          </nav>
          <a
            href={c.hero.primary_cta.href}
            className="hidden rounded-xl bg-red-500 px-4 py-2 text-sm font-semibold text-white shadow hover:bg-red-400 md:block"
          >
            {c.hero.primary_cta.label}
          </a>
        </div>
      </header>

      {/* HERO */}
      <section className="relative overflow-hidden pt-14 md:pt-20">
        <div className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(ellipse_at_top,rgba(239,68,68,0.1),transparent_60%)]" />
        <div className="mx-auto max-w-6xl px-4">
          <motion.div
            variants={fade}
            initial="hidden"
            animate="show"
            transition={{ duration: 0.6, ease: "easeOut" }}
            className="mx-auto max-w-3xl text-center"
          >
            <div className="mb-4 flex flex-wrap items-center justify-center gap-2">
              {c.hero.supporting_badges.map((b, i) => (
                <Badge key={i}>{b}</Badge>
              ))}
            </div>
            <h1 className="text-balance text-3xl font-extrabold tracking-tight text-black md:text-6xl">
              {heroHeadline}
            </h1>
            <p className="mx-auto mt-4 max-w-2xl text-lg text-gray-600 md:text-xl">
              {c.hero.subheadline}
            </p>
            <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <a
                href={c.hero.primary_cta.href}
                className="inline-flex items-center gap-2 rounded-2xl bg-red-500 px-6 py-3 font-semibold text-white shadow-lg shadow-red-500/20 hover:bg-red-400"
              >
                <PlayCircle /> {c.hero.primary_cta.label}
              </a>
              {/*
              <a
                href={c.hero.secondary_cta.href}
                className="inline-flex items-center gap-2 rounded-2xl border border-gray-300 bg-white px-6 py-3 font-semibold text-black hover:bg-gray-50"
              >
                데모 보기 <ArrowRight size={18} />
              </a>*/}
            </div>
          </motion.div>
        </div>
      </section>

      {/* USP Bullets */}
      <Section id="features" title="하루 1분, 습관이 되는 학습" /*subtitle={c.brand.tagline}*/>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {c.usp_bullets.map((u, i) => (
            <div
              key={i}
              className="rounded-3xl border border-gray-200 bg-white p-6 shadow-lg shadow-gray-200/30"
            >
              <div className="flex items-center gap-2 text-black">
                <CheckCircle2 className="text-red-500" />
                <h3 className="font-semibold">{u.title}</h3>
              </div>
              <p className="mt-2 text-gray-600">{u.desc}</p>
            </div>
          ))}
        </div>
      </Section>

      {/* Feature Sections */}
      <Section id="deep" title="핵심 기능" subtitle="학습의 본질을 바꾸는 설계">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {c.feature_sections.map((f) => (
            <div
              key={f.id}
              className="group rounded-3xl border border-gray-200 bg-white p-6 transition hover:-translate-y-1 hover:bg-gray-50"
            >
              <div className="flex items-center gap-2 text-black">
                <Headphones className="text-red-500" />
                <h4 className="font-semibold">{f.title}</h4>
              </div>
              <p className="mt-1 text-gray-600">{f.summary}</p>
              <ul className="mt-3 space-y-2">
                {f.bullets.map((b, i) => (
                  <li key={i} className="flex items-start gap-2 text-gray-600">
                    <CheckCircle2 className="mt-0.5 text-red-500" size={18} />
                    <span>{b}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </Section>

      {/* How it works */}
      <Section id="how" title="이렇게 배워요" subtitle="1분 카드로 이어지는 마이크로러닝">
        <ol className="grid gap-6 md:grid-cols-3">
          {c.how_it_works.map((s) => (
            <li
              key={s.step}
              className="rounded-3xl border border-gray-200 bg-white p-6"
            >
              <div className="text-sm font-semibold text-red-500">STEP {s.step}</div>
              <div className="mt-1 text-lg font-semibold text-black">{s.title}</div>
              <p className="mt-2 text-gray-600">{s.desc}</p>
            </li>
          ))}
        </ol>
        {/* Sample Card and Text Analysis Preview */}
        <div className="mt-12 grid gap-6 md:grid-cols-2">
          {/* Sample Card Preview */}
          <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-lg">
            <div className="mb-4 text-center">
              <h3 className="text-lg font-semibold text-black">예문 카드</h3>
              <p className="mt-1 text-sm text-gray-600">예문 카드는 매일 새롭게 추가됩니다</p>
            </div>
            <div className="flex justify-center">
              <img 
                src="/sample.png" 
                alt="예문 카드 샘플" 
                className="max-w-full h-auto rounded-xl shadow-md"
                style={{ maxHeight: '400px' }}
              />
            </div>
          </div>
          
          {/* Text Analysis Preview */}
          <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-lg">
            <div className="mb-4 text-center">
              <h3 className="text-lg font-semibold text-black">텍스트 분석</h3>
              <p className="mt-1 text-sm text-gray-600">학습할 텍스트를 직접 입력하세요</p>
            </div>
            <div className="flex justify-center">
              <img 
                src="/analysis.png" 
                alt="텍스트 분석 샘플" 
                className="max-w-full h-auto rounded-xl shadow-md"
                style={{ maxHeight: '400px' }}
              />
            </div>
          </div>
        </div>
      </Section>

      {/* Comparison */}
      <Section id="comparison" title={c.comparison.title}>
        <ComparisonTable rows={c.comparison.rows} />
        <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <a
                href={c.hero.secondary_cta.href}
                className="inline-flex items-center gap-2 rounded-2xl bg-red-500 px-6 py-3 font-semibold text-white shadow-lg shadow-red-500/20 hover:bg-red-400"
              >
                <PlayCircle /> {c.hero.secondary_cta.label}
              </a>
              {/*
              <a
                href={c.hero.secondary_cta.href}
                className="inline-flex items-center gap-2 rounded-2xl border border-gray-300 bg-white px-6 py-3 font-semibold text-black hover:bg-gray-50"
              >
                데모 보기 <ArrowRight size={18} />
              </a>*/}
            </div>
      </Section>


      {/* Personas short */}
      <Section
        id="personas"
        title="누구에게 특히 잘 맞나요?"
        subtitle="각자의 목표에 딱 맞춘 개인화 학습"
      >
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {c.personas_short_benefits.map((p, i) => (
            <div key={i} className="rounded-2xl border border-gray-200 bg-white p-4">
              <div className="text-black font-medium">{p.persona}</div>
              <div className="mt-1 text-gray-600">{p.benefit}</div>
            </div>
          ))}
        </div>
      </Section>


      {/* Social Proof */}
      <Section id="reviews" title={c.social_proof.section_title}>
        <div className="grid gap-6 md:grid-cols-2">
          {c.social_proof.reviews.map((r, i) => (
            <div key={i} className="rounded-3xl border border-gray-200 bg-white p-6">
              <div className="mb-2 flex items-center gap-2">
                <Star className="text-red-500" size={18} />
                <div className="text-black font-semibold">
                  {r.name} <span className="text-gray-500">({r.age})</span>
                </div>
                <span className="text-gray-500">· {r.role}</span>
              </div>
              <p className="text-gray-600 leading-relaxed">"{r.quote}"</p>
            </div>
          ))}
        </div>
      </Section>
        
      {/* Metrics */}
      {/*
      <Section id="metrics" title={c.metrics_banner.title}>
        <div className="flex flex-wrap items-center gap-3">
          {c.metrics_banner.bullets.map((m, i) => (
            <Metric key={i} text={m} />
          ))}
        </div>
        <p className="mt-3 text-xs text-gray-500">{c.metrics_banner.disclaimer}</p>
      </Section>*/}


      {/* Pricing */}
      {/*
      <Section id="pricing" title={c.pricing.title} subtitle={c.pricing.guarantee}>
        <div className="grid gap-6 md:grid-cols-3">
          {c.pricing.plans.map((p) => (
            <PriceCard key={p.name} plan={p} />
          ))}
        </div>
      </Section>*/}

      {/* FAQ */}
      {/*
      <Section id="faq" title={c.faq.title}>
        <div className="grid gap-4 md:grid-cols-2">
          {c.faq.items.map((it, i) => (
            <AccordionItem key={i} q={it.q} a={it.a} />
          ))}
        </div>
      </Section>*/}

      {/* CTA */}
      <Section id="cta" title={c.cta_sections[0].title} subtitle={c.cta_sections[0].sub}>
        <div className="flex flex-col items-center justify-center gap-3 sm:flex-row">
          <a
            href={c.cta_sections[0].primary_cta.href}
            className="inline-flex items-center gap-2 rounded-2xl bg-red-500 px-6 py-3 font-semibold text-white shadow-lg shadow-red-500/20 hover:bg-red-400"
          >
            <PlayCircle /> {c.cta_sections[0].primary_cta.label}
          </a>
          {/*
          <a
            href={c.cta_sections[0].secondary_cta.href}
            className="inline-flex items-center gap-2 rounded-2xl border border-gray-300 bg-white px-6 py-3 font-semibold text-black hover:bg-gray-50"
          >
            샘플 세트 보기 <ArrowRight size={18} />
          </a>
          */}
        </div>
      </Section>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-gray-100">
        <div className="mx-auto max-w-6xl px-4 py-10">
          <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
            <div className="flex items-center gap-2">
              <img src="/onigiri.jpg" alt="Onigiri" className="w-6 h-6 rounded-full" />
              <span className="text-black font-semibold">{c.brand.name_ko}</span>
            </div>
            <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
              {c.footer.links.map((l, i) => (
                <a key={i} href={l.href} className="hover:text-black">
                  {l.label}
                </a>
              ))}
            </div>
          </div>
          <div className="mt-6 text-xs text-gray-500">{c.footer.copyright}</div>
        </div>
      </footer>
    </div>
  );
}

export default App;
