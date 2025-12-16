import React, { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { TrendingUp, Wifi, Bot } from "lucide-react";
import { useQuery } from "@tanstack/react-query";

import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import CandlestickChart from "@/components/CandlestickChart";
import { getCandles, explainIndicators } from "@/lib/api";
import { useAuthStore } from "@/stores/authStore";
import { toast } from "sonner";

/* ===============================
   Constants
   =============================== */
const WS_BASE =
  import.meta.env.VITE_WS_BASE_URL || "ws://localhost:8000";

export default function Market() {
  const [symbol, setSymbol] = useState("AAPL");
  const [timeframe, setTimeframe] = useState("5");
  const [livePrice, setLivePrice] = useState<number | null>(null);
  const [aiExplanation, setAiExplanation] = useState<string | null>(null);
  const [explaining, setExplaining] = useState(false);

  const wsRef = useRef<WebSocket | null>(null);
  const { isAuthenticated } = useAuthStore();

  /* ===============================
     LIVE PRICE STREAM (WebSocket)
     =============================== */
  useEffect(() => {
    if (!isAuthenticated || !symbol) {
      wsRef.current?.close();
      return;
    }

    wsRef.current?.close();

    const ws = new WebSocket(`${WS_BASE}/ws/market/${symbol}`);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setLivePrice(data.price);
    };

    ws.onerror = () => {
      toast.error("Live market stream error");
    };

    return () => {
      ws.close();
    };
  }, [symbol, isAuthenticated]);

  /* ===============================
     CANDLESTICKS + INDICATORS (REST)
     =============================== */
  const {
    data: candles,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["candles", symbol, timeframe],
    queryFn: () => getCandles(symbol, timeframe),
    enabled: isAuthenticated && !!symbol,
    staleTime: 60 * 1000,
    retry: false,
  });

  /* ===============================
     Error handling (NO toast spam)
     =============================== */
  useEffect(() => {
    if (error instanceof Error) {
      toast.error("Failed to load market data");
    }
  }, [error]);

  const latestCandle = candles?.[candles.length - 1];

  /* ===============================
     AI Explain Indicators
     =============================== */
  const handleExplain = async () => {
    if (!latestCandle) return;

    setExplaining(true);
    setAiExplanation(null);

    try {
      const res = await explainIndicators({
        symbol,
        price: livePrice ?? latestCandle.close,
        rsi: latestCandle.rsi,
        sma: latestCandle.sma,
        ema: latestCandle.ema,
      });

      setAiExplanation(res.explanation);
    } catch {
      toast.error("Failed to get AI explanation");
    } finally {
      setExplaining(false);
    }
  };

  /* ===============================
     UI
     =============================== */
  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-3xl font-bold mb-2">
          <span className="gradient-text">Market</span>
        </h1>
        <p className="text-muted-foreground">
          Real-time candlestick charts with AI-powered indicator analysis
        </p>
      </motion.div>

      {/* Symbol Input */}
      <Card className="glass p-4 border-border/50 max-w-sm">
        <label className="text-sm text-muted-foreground mb-1 block">
          Asset Symbol
        </label>
        <Input
          value={symbol}
          onChange={(e) => setSymbol(e.target.value.toUpperCase())}
          placeholder="AAPL, TSLA, BTCUSDT"
        />
      </Card>

      {/* Market Card */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <Card className="glass p-6 border-border/50 space-y-4">
          {/* Header Row */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <TrendingUp className="h-6 w-6 text-primary" />
              <h2 className="text-2xl font-semibold">
                {symbol}
                {livePrice && (
                  <span className="ml-2 text-primary">
                    ${livePrice.toFixed(2)}
                  </span>
                )}
              </h2>
            </div>

            <div className="flex items-center gap-1 text-xs text-muted-foreground">
              <Wifi className="h-4 w-4 text-green-500" />
              LIVE
            </div>
          </div>

          {/* Timeframe Selector */}
          <div className="flex gap-2">
            {["1", "5", "15", "60", "D"].map((tf) => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`px-3 py-1 rounded text-sm ${
                  timeframe === tf
                    ? "bg-primary text-white"
                    : "bg-muted text-muted-foreground"
                }`}
              >
                {tf === "D" ? "1D" : `${tf}m`}
              </button>
            ))}
          </div>

          {/* Chart */}
          {isLoading && <Skeleton className="h-[420px] w-full" />}

          {!isLoading && candles && candles.length > 0 && (
            <CandlestickChart data={candles} />
          )}

          {!isLoading && (!candles || candles.length === 0) && (
            <p className="text-muted-foreground text-sm">
              No candle data available for this symbol.
            </p>
          )}

          {/* AI Explain Button */}
          <div className="flex justify-end mt-4">
            <button
              onClick={handleExplain}
              disabled={explaining || !latestCandle?.rsi}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-primary to-secondary text-white text-sm hover:opacity-90 disabled:opacity-50"
            >
              <Bot className="h-4 w-4" />
              {explaining ? "Analyzing…" : "AI Explain Indicators"}
            </button>
          </div>

          {/* AI Explanation */}
          {aiExplanation && (
            <Card className="mt-4 glass p-4 border-border/50">
              <h3 className="font-semibold mb-2 flex items-center gap-2">
                <Bot className="h-4 w-4 text-primary" />
                AI Insight
              </h3>
              <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                {aiExplanation}
              </p>
            </Card>
          )}
        </Card>
      </motion.div>
    </div>
  );
}
