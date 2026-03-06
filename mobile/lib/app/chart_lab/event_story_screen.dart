import 'package:flutter/material.dart';

import 'models/event_card_dto.dart';
import 'widgets/astro_details_sheet.dart';
import 'widgets/story_slide.dart';

class EventStoryScreen extends StatefulWidget {
  const EventStoryScreen({
    super.key,
    required this.card,
    this.timelineSummary,
    this.timelineLines = const <String>[],
  });

  final EventCardDto card;
  final String? timelineSummary;
  final List<String> timelineLines;

  @override
  State<EventStoryScreen> createState() => _EventStoryScreenState();
}

class _EventStoryScreenState extends State<EventStoryScreen> {
  static const int _pageCount = 5;
  late final PageController _controller;
  int _pageIndex = 0;

  @override
  void initState() {
    super.initState();
    _controller = PageController();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final card = widget.card;
    final neOluyor = _firstParagraph(card.conflict);
    final timelineFooter = _timelineFooter();

    return Scaffold(
      appBar: AppBar(title: Text(card.title.isNotEmpty ? card.title : 'Story')),
      body: Stack(
        children: [
          PageView(
            controller: _controller,
            onPageChanged: (index) => setState(() => _pageIndex = index),
            children: [
              StorySlide(title: 'Ne oluyor?', body: neOluyor),
              StorySlide(title: 'Refleks', body: card.shadow),
              StorySlide(title: 'Ustalik', body: card.upper),
              StorySlide(
                title: 'Ne yap?',
                bullets: card.guidance,
                emptyText: 'Bu kartta onerilen adim bulunmuyor.',
              ),
              StorySlide(
                title: 'Dikkat',
                bullets: card.watchOut,
                footer: timelineFooter,
                emptyText: 'Bu kartta dikkat notu bulunmuyor.',
              ),
            ],
          ),
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: Container(
              padding: const EdgeInsets.fromLTRB(16, 10, 16, 16),
              decoration: BoxDecoration(
                color: Theme.of(context).scaffoldBackgroundColor,
                border: const Border(top: BorderSide(color: Colors.black12)),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: Row(
                      children: List<Widget>.generate(
                        _pageCount,
                        (index) => _dot(active: index == _pageIndex),
                      ),
                    ),
                  ),
                  TextButton(
                    onPressed: () {
                      showModalBottomSheet<void>(
                        context: context,
                        isScrollControlled: true,
                        builder: (_) => AstroDetailsSheet(card: card),
                      );
                    },
                    child: const Text('Detaylar'),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _dot({required bool active}) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 180),
      margin: const EdgeInsets.only(right: 6),
      width: active ? 16 : 8,
      height: 8,
      decoration: BoxDecoration(
        color: active ? Colors.black87 : Colors.black26,
        borderRadius: BorderRadius.circular(999),
      ),
    );
  }

  String _firstParagraph(String text) {
    final trimmed = text.trim();
    if (trimmed.isEmpty) {
      return '';
    }
    final byDoubleBreak = trimmed.split('\n\n').first.trim();
    return byDoubleBreak.isEmpty ? trimmed : byDoubleBreak;
  }

  String? _timelineFooter() {
    final parts = <String>[];
    final localSummary = widget.card.timelineSummary.trim();
    if (localSummary.isNotEmpty) {
      parts.add(localSummary);
    } else if ((widget.timelineSummary ?? '').trim().isNotEmpty) {
      parts.add(widget.timelineSummary!.trim());
    }

    final localLines = widget.card.timelineLines.isNotEmpty
        ? widget.card.timelineLines
        : widget.timelineLines;
    if (localLines.isNotEmpty) {
      parts.add(localLines.take(2).join(' • '));
    }
    if (parts.isEmpty) {
      return null;
    }
    return parts.join('\n');
  }
}
