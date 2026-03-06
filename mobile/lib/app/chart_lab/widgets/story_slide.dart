import 'package:flutter/material.dart';

class StorySlide extends StatelessWidget {
  const StorySlide({
    super.key,
    required this.title,
    this.body,
    this.bullets = const <String>[],
    this.footer,
    this.emptyText = 'Bu bolum icin icerik yok.',
  });

  final String title;
  final String? body;
  final List<String> bullets;
  final String? footer;
  final String emptyText;

  @override
  Widget build(BuildContext context) {
    final hasBody = body != null && body!.trim().isNotEmpty;
    final hasBullets = bullets.isNotEmpty;
    final hasFooter = footer != null && footer!.trim().isNotEmpty;

    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 96),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 12),
          if (!hasBody && !hasBullets && !hasFooter)
            Text(
              emptyText,
              style: Theme.of(
                context,
              ).textTheme.bodyMedium?.copyWith(color: Colors.black54),
            ),
          if (hasBody) Text(body!),
          if (hasBullets) ...[
            for (final item in bullets) ...[
              if (item.trim().isNotEmpty)
                Padding(
                  padding: const EdgeInsets.only(top: 8),
                  child: Text('• ${item.trim()}'),
                ),
            ],
          ],
          if (hasFooter) ...[
            const SizedBox(height: 14),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(10),
                color: Colors.black.withValues(alpha: 0.04),
              ),
              child: Text(footer!),
            ),
          ],
        ],
      ),
    );
  }
}
