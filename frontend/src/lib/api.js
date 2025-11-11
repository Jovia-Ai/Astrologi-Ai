import axios from "axios";

const LOCAL_DEFAULT_URL = "http://localhost:5000";
const REMOTE_FALLBACK_URL = "https://astrolog-ai.onrender.com";

const initialBase =
  (import.meta.env?.VITE_API_URL && import.meta.env.VITE_API_URL.trim()) ||
  LOCAL_DEFAULT_URL;

let activeBaseUrl = initialBase.replace(/\/$/, "");

function makeUrl(base, path) {
  if (!path) return base;
  if (path.startsWith("http://") || path.startsWith("https://")) return path;
  const normalizedBase = base.endsWith("/") ? base.slice(0, -1) : base;
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${normalizedBase}${normalizedPath}`;
}

function extractMessage(error) {
  const fallback = "İstek sırasında bir sorun oluştu. Lütfen tekrar dene.";
  if (!error) return fallback;
  const responseMessage =
    error.response?.data?.error ||
    error.response?.data?.message ||
    error.response?.data?.detail;
  if (responseMessage) return responseMessage;
  return error.message || fallback;
}

async function request(method, path, payload, attempt = 0) {
  const url = makeUrl(activeBaseUrl, path);
  try {
    const response = await axios({
      method,
      url,
      data: payload,
      headers: { "Content-Type": "application/json" },
      timeout: 15000,
    });
    return response.data;
  } catch (error) {
    const isNetworkError =
      !error.response &&
      (error.code === "ERR_NETWORK" ||
        error.message === "Network Error" ||
        /Network Error/i.test(error.message || ""));

    const canRetry =
      attempt === 0 &&
      isNetworkError &&
      activeBaseUrl === LOCAL_DEFAULT_URL;

    if (canRetry) {
      console.warn(
        "⚠️ Local API unreachable, falling back to hosted API:",
        REMOTE_FALLBACK_URL
      );
      activeBaseUrl = REMOTE_FALLBACK_URL;
      return request(method, path, payload, attempt + 1);
    }

    console.error(`❌ API Error on ${path}:`, error.response?.data || error.message);

    if (method === "get" && error.response?.status === 404) {
      return null;
    }
    throw new Error(extractMessage(error));
  }
}

const post = (path, payload) => request("post", path, payload);
const put = (path, payload) => request("put", path, payload);
const get = (path) => request("get", path);

export const calculateNatalChart = (payload) => post("/natal-chart", payload);

const buildLifeBundle = (data, strategy = "primary") => {
  const story = data?.life_narrative || null;
  const meta = data?.meta || null;
  const legacy =
    data?.life_legacy ||
    data?.archetype?.life_narrative ||
    null;
  return {
    story,
    meta,
    legacy,
    strategy,
  };
};

export const getInterpretation = async (chartData) => {
  let preparedChart = chartData;
  if (typeof preparedChart === "string") {
    try {
      preparedChart = JSON.parse(preparedChart);
    } catch (error) {
      console.warn("Unable to parse chart data string:", error);
      preparedChart = null;
    }
  }

  if (!preparedChart || typeof preparedChart !== "object") {
    console.warn("Invalid chart data supplied to getInterpretation", chartData);
  }

  const data = await post("/interpretation", {
    chart: preparedChart,
    chart_data: preparedChart,
  });

  const bundle = buildLifeBundle(data);
  const legacyText = bundle?.legacy?.text || data?.text || "";
  const prepared = {
    ...data,
    life_bundle: bundle,
  };

  if (!data?.cards?.life) {
    const fallbackCard = {
      title: "Hayat Anlatısı",
      narrative: { main: legacyText },
      reasons: { psychology: [] },
      actions: [],
      tags: [],
      confidence_label: "Dengeli",
    };
    prepared.cards = {
      ...(data?.cards || {}),
      life: fallbackCard,
    };
  }

  return prepared;
};

export const getAlternateNarrative = async (chartData, strategy = "secondary") => {
  const preparedChart =
    typeof chartData === "string"
      ? (() => {
          try {
            return JSON.parse(chartData);
          } catch (error) {
            console.warn("Unable to parse chart data string:", error);
            return null;
          }
        })()
      : chartData;

  const data = await post("/interpretation", {
    chart: preparedChart,
    chart_data: preparedChart,
    alt_strategy: strategy,
  });

  return buildLifeBundle(data, strategy);
};

export const calculateSynastry = (payload) =>
  post("/calculate_synastry_chart", payload);

export const saveUserProfile = (profile) => post("/api/profile", profile);

export const fetchUserProfile = async (email) => {
  if (!email) {
    throw new Error("Profil için e-posta sağlanmalı.");
  }
  const result = await get(`/api/profile?email=${encodeURIComponent(email)}`);
  if (!result) return null;
  if (result.profile !== undefined) {
    return result.profile;
  }
  return result;
};

export const updateUserProfile = (profile) => put("/api/profile", profile);

export const sendChatMessage = async (message, chartData) => {
  try {
    const response = await post("/chat/message", { message, chart: chartData });
    return response.reply;
  } catch (error) {
    console.error("Chat error:", error);
    return "Üzgünüm, şu anda yanıt veremiyorum.";
  }
};
