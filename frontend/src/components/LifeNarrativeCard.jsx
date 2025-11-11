import { useState } from "react";
import {
  Badge,
  Box,
  Button,
  Collapse,
  Divider,
  HStack,
  Stack,
  Text,
  VStack,
  Wrap,
  WrapItem,
} from "@chakra-ui/react";
import { sanitize } from "../lib/format.js";

const formatConfidence = (value) => {
  if (typeof value !== "number" || Number.isNaN(value)) return null;
  const percentage = Math.round(Math.min(1, value) * 100);
  return `${percentage}% güven`;
};

const LifeNarrativeCard = ({ story, meta, title = "💎 Life Narrative" }) => {
  const [showMeta, setShowMeta] = useState(false);

  const headline = sanitize(story?.headline) || "İç Sesinin İzinde";
  const summary = sanitize(story?.summary) || "İçgörü henüz hazır değil.";
  const reasons = Array.isArray(story?.reasons)
    ? story.reasons.map((item, index) => ({
        key: `reason-${index}`,
        text: sanitize(item),
      })).filter((item) => item.text)
    : [];
  const actions = Array.isArray(story?.actions)
    ? story.actions.map((item, index) => ({
        key: `action-${index}`,
        text: sanitize(item),
      })).filter((item) => item.text)
    : [];
  const storyThemes = Array.isArray(story?.themes)
    ? story.themes.map((item) => sanitize(item)).filter(Boolean)
    : [];

  const axis = sanitize(meta?.axis) || "—";
  const focus = sanitize(meta?.focus) || "—";
  const metaThemes = Array.isArray(meta?.themes)
    ? meta.themes.map((item) => sanitize(item)).filter(Boolean)
    : [];
  const derived = Array.isArray(meta?.derived_from) ? meta.derived_from : [];
  const correlations =
    meta?.correlations && typeof meta.correlations === "object"
      ? meta.correlations
      : {};
  const confidenceLabel = formatConfidence(meta?.confidence);
  const correlationEntries = [
    { label: "Element dengesi", value: correlations?.element_balance },
    { label: "Modalite dengesi", value: correlations?.modality_balance },
    { label: "Baskın gezegen", value: correlations?.dominant_planet },
    { label: "Enerji deseni", value: correlations?.dominant_cluster },
    { label: "Polar eksen", value: correlations?.polar_axis },
  ].filter((item) => item.value);

  return (
    <Box
      borderRadius="28px"
      p={{ base: 6, md: 8 }}
      bg="rgba(255,255,255,0.95)"
      boxShadow="soft"
    >
      <Stack spacing={4}>
        <Text fontWeight="700" fontSize="lg">
          {title}
        </Text>
        <VStack spacing={1} align="flex-start">
          <Text fontSize="xl" fontWeight="700">
            {headline}
          </Text>
          <Text color="rgba(30,27,41,0.78)" lineHeight="taller">
            {summary}
          </Text>
        </VStack>

        {reasons.length > 0 && (
          <Box>
            <Text fontWeight="600" fontSize="sm" color="rgba(30,27,41,0.65)" mb={2}>
              Psikolojik gerekçeler
            </Text>
            <Stack spacing={2}>
              {reasons.map((item) => (
                <Text key={item.key} color="rgba(30,27,41,0.78)" lineHeight="tall">
                  • {item.text}
                </Text>
              ))}
            </Stack>
          </Box>
        )}

        {actions.length > 0 && (
          <Box>
            <Text fontWeight="600" fontSize="sm" color="rgba(30,27,41,0.65)" mb={2}>
              Uygulanabilir adımlar
            </Text>
            <Stack spacing={2}>
              {actions.map((item) => (
                <Badge
                  key={item.key}
                  variant="subtle"
                  colorScheme="teal"
                  borderRadius="lg"
                  px={3}
                  py={1}
                  fontWeight="600"
                >
                  {item.text}
                </Badge>
              ))}
            </Stack>
          </Box>
        )}

        {storyThemes.length > 0 && (
          <Box>
            <Text fontWeight="600" fontSize="sm" color="rgba(30,27,41,0.65)" mb={2}>
              Temalar
            </Text>
            <Wrap spacing={2}>
              {storyThemes.map((theme) => (
                <WrapItem key={theme}>
                  <Badge variant="solid" colorScheme="purple" borderRadius="lg" px={3} py={1}>
                    {theme}
                  </Badge>
                </WrapItem>
              ))}
            </Wrap>
          </Box>
        )}

        <HStack spacing={3} flexWrap="wrap">
          <Badge colorScheme="purple" borderRadius="full" px={3} py={1}>
            Eksen bilgisi panelde
          </Badge>
          <Badge colorScheme="pink" borderRadius="full" px={3} py={1}>
            Odak bilgisi panelde
          </Badge>
          {confidenceLabel && (
            <Badge colorScheme="blue" borderRadius="full" px={3} py={1}>
              {confidenceLabel}
            </Badge>
          )}
        </HStack>
        <Button
          onClick={() => setShowMeta((prev) => !prev)}
          variant="ghost"
          size="sm"
          alignSelf="flex-start"
        >
          {showMeta ? "Kaynakları gizle" : "Nasıl hesaplandı?"}
        </Button>
        <Collapse in={showMeta} animateOpacity>
          <Stack
            spacing={4}
            bg="rgba(246,247,251,0.7)"
            borderRadius="20px"
            p={4}
            border="1px solid rgba(219,225,255,0.7)"
          >
              <HStack spacing={3} flexWrap="wrap">
                <Badge colorScheme="purple" borderRadius="full" px={3} py={1}>
                  Eksen: {axis}
                </Badge>
                <Badge colorScheme="pink" borderRadius="full" px={3} py={1}>
                  İlgi: {focus}
                </Badge>
                {confidenceLabel && (
                  <Badge colorScheme="blue" borderRadius="full" px={3} py={1}>
                    {confidenceLabel}
                  </Badge>
                )}
              </HStack>

              {metaThemes.length > 0 && (
                <Box>
                  <Text fontWeight="600" fontSize="sm" color="rgba(30,27,41,0.65)" mb={2}>
                    Panel temaları
                  </Text>
                  <Wrap spacing={2}>
                    {metaThemes.map((theme) => (
                      <WrapItem key={`meta-${theme}`}>
                        <Badge variant="subtle" borderRadius="lg" px={3} py={1}>
                          {theme}
                        </Badge>
                      </WrapItem>
                    ))}
                  </Wrap>
                </Box>
              )}

              <Divider borderColor="rgba(30,27,41,0.08)" />
              <Box>
                <Text fontWeight="600" fontSize="sm" color="rgba(30,27,41,0.65)" mb={2}>
                  Kaynak açı/gezegen çiftleri
                </Text>
                {derived.length ? (
                  <VStack align="flex-start" spacing={1} fontSize="sm" color="rgba(30,27,41,0.7)">
                    {derived.slice(0, 8).map((item, index) => (
                      <Text key={`${item.pair}-${index}`}>
                        {sanitize(item.pair) || "—"} • {sanitize(item.aspect) || "—"}
                        {typeof item.orb === "number" ? ` • orb ${item.orb}°` : ""}
                      </Text>
                    ))}
                  </VStack>
                ) : (
                  <Text fontSize="sm" color="rgba(30,27,41,0.55)">
                    Kaynak açı verisi sağlanmadı.
                  </Text>
                )}
              </Box>

              {correlationEntries.length > 0 && (
                <>
                  <Divider borderColor="rgba(30,27,41,0.08)" />
                  <Box>
                    <Text fontWeight="600" fontSize="sm" color="rgba(30,27,41,0.65)" mb={2}>
                      Korelasyonlar
                    </Text>
                    <VStack align="flex-start" spacing={1} fontSize="sm" color="rgba(30,27,41,0.7)">
                      {correlationEntries.map((entry) => {
                        const valueText =
                          typeof entry.value === "number"
                            ? String(entry.value)
                            : entry.value || "";
                        return (
                          <Text key={entry.label}>
                            {entry.label}: {sanitize(valueText) || "—"}
                          </Text>
                        );
                      })}
                    </VStack>
                  </Box>
                </>
              )}
          </Stack>
        </Collapse>
      </Stack>
    </Box>
  );
};

export default LifeNarrativeCard;
