import React from "react";
import ReactDOM from "react-dom/client";
import { Activity, AlertTriangle, BarChart3, Download, FileUp, Gauge, Scale } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import "./styles.css";

type GroupMetric = {
  group: string;
  count: number;
  selection_rate: number;
  true_positive_rate: number | null;
  false_positive_rate: number | null;
  accuracy: number | null;
};

type MitigationResult = {
  strategy: string;
  accuracy: number | null;
  demographic_parity_difference: number;
  equal_opportunity_difference: number | null;
  notes: string;
};

type AuditResponse = {
  audit_id: string;
  dataset_rows: number;
  protected_attribute: string;
  target: string;
  metrics: {
    reference_group: string;
    disparate_impact_ratio: number | null;
    demographic_parity_difference: number;
    equal_opportunity_difference: number | null;
    equalized_odds_difference: number | null;
    group_metrics: GroupMetric[];
  };
  mitigation: MitigationResult[];
  explanations: { feature: string; impact: number; direction: string }[];
  plain_english_summary: string;
};

type BenchmarkResponse = {
  results: {
    model_name: string;
    accuracy: number;
    disparate_impact_ratio: number | null;
    demographic_parity_difference: number;
    equal_opportunity_difference: number | null;
    notes: string;
  }[];
};

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

function percent(value: number | null) {
  if (value === null) return "n/a";
  return `${(value * 100).toFixed(1)}%`;
}

function MetricTile({
  label,
  value,
  tone
}: {
  label: string;
  value: string;
  tone: "neutral" | "warn" | "good";
}) {
  const toneClass = {
    neutral: "border-slate-200 bg-white",
    warn: "border-amber-300 bg-amber-50",
    good: "border-emerald-300 bg-emerald-50"
  }[tone];

  return (
    <section className={`rounded-md border p-4 shadow-sm ${toneClass}`}>
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-civic-ink">{value}</p>
    </section>
  );
}

function App() {
  const [audit, setAudit] = React.useState<AuditResponse | null>(null);
  const [protectedAttribute, setProtectedAttribute] = React.useState("district");
  const [benchmark, setBenchmark] = React.useState<BenchmarkResponse | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const fileInputRef = React.useRef<HTMLInputElement | null>(null);
  const modelDatasetInputRef = React.useRef<HTMLInputElement | null>(null);
  const modelFileInputRef = React.useRef<HTMLInputElement | null>(null);
  const pendingModelDatasetRef = React.useRef<File | null>(null);

  async function runAudit(attribute = protectedAttribute) {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/audit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ protected_attribute: attribute })
      });
      if (!response.ok) throw new Error(await response.text());
      setAudit(await response.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to run audit");
    } finally {
      setLoading(false);
    }
  }

  async function runBenchmark(attribute = protectedAttribute) {
    try {
      const response = await fetch(`${API_URL}/benchmark/sample?protected_attribute=${attribute}`);
      if (response.ok) setBenchmark(await response.json());
    } catch {
      setBenchmark(null);
    }
  }

  async function uploadCsv(file: File) {
    setLoading(true);
    setError(null);
    const form = new FormData();
    form.append("file", file);
    form.append("protected_attribute", protectedAttribute);
    form.append("target", "approved");
    form.append("score_column", "model_score");
    try {
      const response = await fetch(`${API_URL}/audit/upload`, {
        method: "POST",
        body: form
      });
      if (!response.ok) throw new Error(await response.text());
      setAudit(await response.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to upload CSV");
    } finally {
      setLoading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  async function uploadModelAudit(dataset: File, modelFile: File) {
    setLoading(true);
    setError(null);
    const form = new FormData();
    form.append("dataset", dataset);
    form.append("model_file", modelFile);
    form.append("protected_attribute", protectedAttribute);
    form.append("target", "approved");
    try {
      const response = await fetch(`${API_URL}/audit/model-upload`, {
        method: "POST",
        body: form
      });
      if (!response.ok) throw new Error(await response.text());
      setAudit(await response.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to audit uploaded model");
    } finally {
      setLoading(false);
      pendingModelDatasetRef.current = null;
      if (modelDatasetInputRef.current) modelDatasetInputRef.current.value = "";
      if (modelFileInputRef.current) modelFileInputRef.current.value = "";
    }
  }

  React.useEffect(() => {
    runAudit("district");
    runBenchmark("district");
  }, []);

  const chartRows =
    audit?.metrics.group_metrics.map((row) => ({
      group: row.group,
      selection: Number((row.selection_rate * 100).toFixed(1)),
      accuracy: row.accuracy === null ? null : Number((row.accuracy * 100).toFixed(1))
    })) ?? [];

  const di = audit?.metrics.disparate_impact_ratio ?? null;

  return (
    <main className="min-h-screen bg-slate-50 text-civic-ink">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-5 py-5 md:flex-row md:items-center md:justify-between">
          <div>
            <div className="flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center rounded-md bg-civic-teal text-white">
                <Scale size={22} />
              </span>
              <div>
                <h1 className="text-2xl font-semibold">CivicPulse</h1>
                <p className="text-sm text-slate-600">Algorithmic fairness audit workspace</p>
              </div>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            {["district", "income_band", "age_band"].map((attribute) => (
              <button
                key={attribute}
                className={`rounded-md border px-3 py-2 text-sm font-medium ${
                  protectedAttribute === attribute
                    ? "border-civic-teal bg-civic-teal text-white"
                    : "border-slate-300 bg-white text-slate-700"
                }`}
                onClick={() => {
                  setProtectedAttribute(attribute);
                  runAudit(attribute);
                  runBenchmark(attribute);
                }}
              >
                {attribute.replace("_", " ")}
              </button>
            ))}
            <button
              className="inline-flex items-center gap-2 rounded-md border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700"
              type="button"
              title="Upload a CSV with approved, model_score, and protected-attribute columns"
              onClick={() => fileInputRef.current?.click()}
            >
              <FileUp size={16} />
              CSV
            </button>
            <input
              ref={fileInputRef}
              className="hidden"
              type="file"
              accept=".csv"
              onChange={(event) => {
                const file = event.target.files?.[0];
                if (file) uploadCsv(file);
              }}
            />
            <button
              className="inline-flex items-center gap-2 rounded-md border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700"
              type="button"
              title="Upload a CSV dataset, then a .pkl, .pickle, or .joblib model"
              onClick={() => modelDatasetInputRef.current?.click()}
            >
              <FileUp size={16} />
              Model
            </button>
            <input
              ref={modelDatasetInputRef}
              className="hidden"
              type="file"
              accept=".csv"
              onChange={(event) => {
                const file = event.target.files?.[0];
                if (file) {
                  pendingModelDatasetRef.current = file;
                  modelFileInputRef.current?.click();
                }
              }}
            />
            <input
              ref={modelFileInputRef}
              className="hidden"
              type="file"
              accept=".pkl,.pickle,.joblib"
              onChange={(event) => {
                const modelFile = event.target.files?.[0];
                const dataset = pendingModelDatasetRef.current;
                if (dataset && modelFile) uploadModelAudit(dataset, modelFile);
              }}
            />
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-5 py-6">
        {error && (
          <div className="mb-4 rounded-md border border-red-300 bg-red-50 p-4 text-sm text-red-800">{error}</div>
        )}

        <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <MetricTile
            label="Disparate impact"
            value={di === null ? "n/a" : di.toFixed(2)}
            tone={di !== null && di < 0.8 ? "warn" : "good"}
          />
          <MetricTile
            label="Parity gap"
            value={audit ? percent(audit.metrics.demographic_parity_difference) : "loading"}
            tone="neutral"
          />
          <MetricTile
            label="Opportunity gap"
            value={audit ? percent(audit.metrics.equal_opportunity_difference) : "loading"}
            tone="neutral"
          />
          <MetricTile
            label="Rows audited"
            value={audit ? String(audit.dataset_rows) : "loading"}
            tone="neutral"
          />
        </section>

        <section className="mt-6 grid min-w-0 gap-5 lg:grid-cols-[1.5fr_1fr]">
          <div className="min-w-0 rounded-md border border-slate-200 bg-white p-4 shadow-sm">
            <div className="mb-4 flex items-center gap-2">
              <BarChart3 size={18} />
              <h2 className="text-lg font-semibold">Decision Rates By Group</h2>
            </div>
            <div className="h-72 min-w-0 sm:h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartRows}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="group" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="selection" name="Selection rate %" fill="#155e75" isAnimationActive={false} />
                  <Bar dataKey="accuracy" name="Accuracy %" fill="#b45309" isAnimationActive={false} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-4 overflow-x-auto">
              <table className="w-full min-w-[360px] border-collapse text-sm">
                <thead>
                  <tr className="border-b text-left text-slate-500">
                    <th className="py-2">Group</th>
                    <th className="py-2">Applicants</th>
                    <th className="py-2">Selection Rate</th>
                    <th className="hidden py-2 sm:table-cell">TPR</th>
                    <th className="hidden py-2 sm:table-cell">FPR</th>
                    <th className="hidden py-2 md:table-cell">Accuracy</th>
                  </tr>
                </thead>
                <tbody>
                  {audit?.metrics.group_metrics.map((item) => (
                    <tr key={item.group} className="border-b border-slate-100">
                      <td className="py-2 pr-3 font-medium">{item.group}</td>
                      <td className="py-2">{item.count}</td>
                      <td className="py-2">{percent(item.selection_rate)}</td>
                      <td className="hidden py-2 sm:table-cell">{percent(item.true_positive_rate)}</td>
                      <td className="hidden py-2 sm:table-cell">{percent(item.false_positive_rate)}</td>
                      <td className="hidden py-2 md:table-cell">{percent(item.accuracy)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <aside className="min-w-0 rounded-md border border-slate-200 bg-white p-4 shadow-sm">
            <div className="mb-3 flex items-center gap-2">
              <AlertTriangle size={18} />
              <h2 className="text-lg font-semibold">Plain-English Finding</h2>
            </div>
            <p className="text-sm leading-6 text-slate-700">
              {loading ? "Running audit..." : audit?.plain_english_summary}
            </p>
          </aside>
        </section>

        <section className="mt-6 grid min-w-0 gap-5 lg:grid-cols-2">
          <div className="min-w-0 rounded-md border border-slate-200 bg-white p-4 shadow-sm">
            <div className="mb-4 flex items-center gap-2">
              <Gauge size={18} />
              <h2 className="text-lg font-semibold">Mitigation Simulator</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[420px] border-collapse text-sm">
                <thead>
                  <tr className="border-b text-left text-slate-500">
                    <th className="py-2">Strategy</th>
                    <th className="py-2">Accuracy</th>
                    <th className="py-2">Parity Gap</th>
                    <th className="py-2">Opportunity Gap</th>
                  </tr>
                </thead>
                <tbody>
                  {audit?.mitigation.map((item) => (
                    <tr key={item.strategy} className="border-b border-slate-100">
                      <td className="py-3 pr-3 font-medium">{item.strategy}</td>
                      <td className="py-3">{percent(item.accuracy)}</td>
                      <td className="py-3">{percent(item.demographic_parity_difference)}</td>
                      <td className="py-3">{percent(item.equal_opportunity_difference)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="min-w-0 rounded-md border border-slate-200 bg-white p-4 shadow-sm">
            <div className="mb-4 flex items-center gap-2">
              <Activity size={18} />
              <h2 className="text-lg font-semibold">Feature Gap Signals</h2>
            </div>
            <div className="space-y-3">
              {audit?.explanations.map((item) => (
                <div key={item.feature} className="rounded-md border border-slate-200 p-3">
                  <div className="flex items-center justify-between gap-3">
                    <p className="min-w-0 break-words font-medium">{item.feature}</p>
                    <span className="text-sm text-slate-500">{item.impact.toFixed(2)}</span>
                  </div>
                  <p className="mt-1 text-sm text-slate-600">{item.direction}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="mt-6 min-w-0 rounded-md border border-slate-200 bg-white p-4 shadow-sm">
          <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div className="flex items-center gap-2">
              <Scale size={18} />
              <h2 className="text-lg font-semibold">Model Benchmark</h2>
            </div>
            <div className="flex flex-wrap gap-2">
              <a
                className="inline-flex items-center gap-2 rounded-md border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700"
                href={`${API_URL}/exports/group-metrics.csv?protected_attribute=${protectedAttribute}`}
              >
                <Download size={16} />
                Groups
              </a>
              <a
                className="inline-flex items-center gap-2 rounded-md border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700"
                href={`${API_URL}/exports/mitigation-results.csv?protected_attribute=${protectedAttribute}`}
              >
                <Download size={16} />
                Mitigation
              </a>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[620px] border-collapse text-sm">
              <thead>
                <tr className="border-b text-left text-slate-500">
                  <th className="py-2">Model</th>
                  <th className="py-2">Accuracy</th>
                  <th className="py-2">Disparate Impact</th>
                  <th className="py-2">Parity Gap</th>
                  <th className="py-2">Notes</th>
                </tr>
              </thead>
              <tbody>
                {benchmark?.results.map((item) => (
                  <tr key={item.model_name} className="border-b border-slate-100">
                    <td className="py-3 pr-3 font-medium">{item.model_name}</td>
                    <td className="py-3">{percent(item.accuracy)}</td>
                    <td className="py-3">
                      {item.disparate_impact_ratio === null ? "n/a" : item.disparate_impact_ratio.toFixed(2)}
                    </td>
                    <td className="py-3">{percent(item.demographic_parity_difference)}</td>
                    <td className="py-3 text-slate-600">{item.notes}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </main>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
