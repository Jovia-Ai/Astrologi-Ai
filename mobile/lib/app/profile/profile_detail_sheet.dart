import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'package:mobile/app/timing/turkish_text.dart';

@immutable
class ProfileDetailSheetData {
  const ProfileDetailSheetData({
    required this.eyebrow,
    required this.headline,
    this.body = '',
    this.placement = '',
    this.accent = const Color(0xFFCAFF4D),
    this.accentInk = const Color(0xFF1A3300),
    this.highlight = '',
    this.chips = const <String>[],
    this.growthNote = '',
    this.ctaLabel,
    this.onCta,
  });

  final String eyebrow;
  final String headline;
  final String body;
  final String placement;
  final Color accent;
  final Color accentInk;
  final String highlight;
  final List<String> chips;
  final String growthNote;
  final String? ctaLabel;
  final VoidCallback? onCta;
}

Future<void> showProfileDetailSheet(
  BuildContext context,
  ProfileDetailSheetData data,
) {
  HapticFeedback.selectionClick();
  return showModalBottomSheet<void>(
    context: context,
    isScrollControlled: true,
    backgroundColor: Colors.transparent,
    barrierColor: const Color.fromRGBO(0, 0, 0, 0.45),
    useSafeArea: true,
    builder: (ctx) => _ProfileDetailSheet(data: data),
  );
}

class _ProfileDetailSheet extends StatelessWidget {
  const _ProfileDetailSheet({required this.data});

  final ProfileDetailSheetData data;

  @override
  Widget build(BuildContext context) {
    final media = MediaQuery.of(context);
    return ConstrainedBox(
      constraints: BoxConstraints(maxHeight: media.size.height * 0.92),
      child: Container(
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
          border: Border(
            top: BorderSide(color: Color.fromRGBO(0, 0, 0, 0.08)),
          ),
        ),
        padding: EdgeInsets.only(bottom: media.viewInsets.bottom),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Padding(
              padding: const EdgeInsets.only(top: 10, bottom: 6),
              child: Container(
                width: 38,
                height: 4,
                decoration: BoxDecoration(
                  color: const Color(0xFFE1E1E1),
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            Flexible(
              child: SingleChildScrollView(
                padding: const EdgeInsets.fromLTRB(20, 14, 20, 28),
                child: _SheetBody(data: data),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SheetBody extends StatelessWidget {
  const _SheetBody({required this.data});

  final ProfileDetailSheetData data;

  @override
  Widget build(BuildContext context) {
    final highlightVisible =
        data.highlight.trim().isNotEmpty &&
        data.headline.contains(data.highlight);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Container(
              width: 6,
              height: 6,
              decoration: BoxDecoration(color: data.accent, shape: BoxShape.circle),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                turkishToUpper(data.eyebrow),
                style: const TextStyle(
                  color: Color(0xFF9A9A9A),
                  fontSize: 9,
                  letterSpacing: 0.8,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
            _CloseButton(onTap: () => Navigator.of(context).maybePop()),
          ],
        ),
        if (data.placement.trim().isNotEmpty) ...[
          const SizedBox(height: 14),
          Text(
            data.placement,
            style: TextStyle(
              color: data.accent,
              fontSize: 9,
              letterSpacing: 0.8,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
        if (data.headline.trim().isNotEmpty) ...[
          const SizedBox(height: 14),
          if (highlightVisible)
            _HighlightHeadline(
              text: data.headline,
              highlight: data.highlight,
              accent: data.accent,
              accentInk: data.accentInk,
            )
          else
            Text(
              data.headline,
              style: const TextStyle(
                color: Color(0xFF111111),
                fontSize: 24,
                height: 1.3,
                letterSpacing: -0.4,
                fontWeight: FontWeight.w400,
              ),
            ),
        ],
        if (data.body.trim().isNotEmpty) ...[
          const SizedBox(height: 14),
          Text(
            data.body,
            style: const TextStyle(
              color: Color(0xFF3F3F3F),
              fontSize: 14.5,
              height: 1.6,
              fontWeight: FontWeight.w400,
            ),
          ),
        ],
        if (data.chips.isNotEmpty) ...[
          const SizedBox(height: 18),
          Wrap(
            spacing: 6,
            runSpacing: 6,
            children: [
              for (final chip in data.chips)
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 5,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.transparent,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                      color: data.accent.withValues(alpha: 0.32),
                    ),
                  ),
                  child: Text(
                    chip,
                    style: TextStyle(
                      color: data.accentInk,
                      fontSize: 10,
                      fontWeight: FontWeight.w400,
                    ),
                  ),
                ),
            ],
          ),
        ],
        if (data.growthNote.trim().isNotEmpty) ...[
          const SizedBox(height: 20),
          _GrowthNote(note: data.growthNote),
        ],
        if ((data.ctaLabel ?? '').trim().isNotEmpty) ...[
          const SizedBox(height: 22),
          _SheetCta(
            label: data.ctaLabel!,
            onTap: () {
              final onCta = data.onCta;
              Navigator.of(context).maybePop();
              if (onCta != null) {
                onCta();
              }
            },
          ),
        ],
      ],
    );
  }
}

class _HighlightHeadline extends StatelessWidget {
  const _HighlightHeadline({
    required this.text,
    required this.highlight,
    required this.accent,
    required this.accentInk,
  });

  final String text;
  final String highlight;
  final Color accent;
  final Color accentInk;

  @override
  Widget build(BuildContext context) {
    final index = text.indexOf(highlight);
    final before = index > 0 ? text.substring(0, index) : '';
    final after = text.substring(index + highlight.length);
    return Text.rich(
      TextSpan(
        style: const TextStyle(
          color: Color(0xFF111111),
          fontSize: 24,
          height: 1.3,
          letterSpacing: -0.4,
          fontWeight: FontWeight.w400,
        ),
        children: [
          if (before.isNotEmpty) TextSpan(text: before),
          TextSpan(
            text: highlight,
            style: TextStyle(backgroundColor: accent, color: accentInk),
          ),
          if (after.isNotEmpty) TextSpan(text: after),
        ],
      ),
    );
  }
}

class _GrowthNote extends StatelessWidget {
  const _GrowthNote({required this.note});

  final String note;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color.fromRGBO(0, 0, 0, 0.07)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 2.5,
            height: 36,
            margin: const EdgeInsets.only(right: 12, top: 2),
            color: const Color(0xFFCAFF4D),
          ),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'AÇILAN KAPI',
                  style: TextStyle(
                    color: Color(0xFF3B6D11),
                    fontSize: 9,
                    letterSpacing: 0.8,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  note,
                  style: const TextStyle(
                    color: Color(0xFF111111),
                    fontSize: 13.5,
                    height: 1.5,
                    fontWeight: FontWeight.w400,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _CloseButton extends StatelessWidget {
  const _CloseButton({required this.onTap});

  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: const Color(0xFFF2F2F2),
      shape: const CircleBorder(),
      child: InkWell(
        customBorder: const CircleBorder(),
        onTap: onTap,
        child: const SizedBox(
          width: 32,
          height: 32,
          child: Icon(Icons.close_rounded, size: 17, color: Color(0xFF555555)),
        ),
      ),
    );
  }
}

class _SheetCta extends StatelessWidget {
  const _SheetCta({required this.label, required this.onTap});

  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      child: Material(
        color: const Color(0xFF111111),
        borderRadius: BorderRadius.circular(22),
        child: InkWell(
          borderRadius: BorderRadius.circular(22),
          onTap: onTap,
          child: Container(
            padding: const EdgeInsets.symmetric(vertical: 14),
            alignment: Alignment.center,
            child: Text(
              label,
              style: const TextStyle(
                color: Color(0xFFCAFF4D),
                fontSize: 13,
                fontWeight: FontWeight.w500,
                letterSpacing: 0.2,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
