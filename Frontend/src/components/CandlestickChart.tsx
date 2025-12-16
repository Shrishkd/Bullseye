import { useEffect, useRef } from "react";
import {
  createChart,
  CandlestickSeries,
  LineSeries,
  UTCTimestamp,
} from "lightweight-charts";

interface Candle {
  time: number; // milliseconds from backend
  open: number;
  high: number;
  low: number;
  close: number;
  sma?: number;
  ema?: number;
  rsi?: number;
}

export default function CandlestickChart({ data }: { data: Candle[] }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!ref.current || !data.length) return;

    ref.current.innerHTML = "";

    const chart = createChart(ref.current, {
      height: 520,
      layout: {
        background: { color: "transparent" },
        textColor: "#aaa",
      },
      grid: {
        vertLines: { color: "#222" },
        horzLines: { color: "#222" },
      },
      rightPriceScale: {
        scaleMargins: { top: 0.1, bottom: 0.35 },
      },
    });

    // ===== Series =====
    const candleSeries = chart.addSeries(CandlestickSeries);

    const smaSeries = chart.addSeries(LineSeries, {
      color: "#4ade80",
      lineWidth: 2,
    });

    const emaSeries = chart.addSeries(LineSeries, {
      color: "#60a5fa",
      lineWidth: 2,
    });

    const rsiSeries = chart.addSeries(LineSeries, {
      color: "#facc15",
      lineWidth: 2,
      priceScaleId: "rsi",
    });

    chart.priceScale("rsi").applyOptions({
      scaleMargins: { top: 0.75, bottom: 0 },
    });

    // ===== Data mapping (CRITICAL FIX) =====
    candleSeries.setData(
      data.map((d) => ({
        time: Math.floor(d.time / 1000) as UTCTimestamp,
        open: d.open,
        high: d.high,
        low: d.low,
        close: d.close,
      }))
    );

    smaSeries.setData(
      data
        .filter((d) => d.sma !== null && d.sma !== undefined)
        .map((d) => ({
          time: Math.floor(d.time / 1000) as UTCTimestamp,
          value: d.sma!,
        }))
    );

    emaSeries.setData(
      data
        .filter((d) => d.ema !== null && d.ema !== undefined)
        .map((d) => ({
          time: Math.floor(d.time / 1000) as UTCTimestamp,
          value: d.ema!,
        }))
    );

    rsiSeries.setData(
      data
        .filter((d) => d.rsi !== null && d.rsi !== undefined)
        .map((d) => ({
          time: Math.floor(d.time / 1000) as UTCTimestamp,
          value: d.rsi!,
        }))
    );

    chart.timeScale().fitContent();

    return () => {
      chart.remove();
    };
  }, [data]);

  return <div ref={ref} className="w-full" />;
}
