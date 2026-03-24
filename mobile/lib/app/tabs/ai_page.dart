import 'package:flutter/material.dart';

import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_assets.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';

class AiPage extends StatefulWidget {
  const AiPage({super.key});

  @override
  State<AiPage> createState() => _AiPageState();
}

class _AiPageState extends State<AiPage> {
  final TextEditingController _composerController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final List<_AiChatMessageData> _messages = <_AiChatMessageData>[];

  @override
  void dispose() {
    _composerController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _sendDraft() {
    final text = _composerController.text.trim();
    if (text.isEmpty) {
      return;
    }
    final timestamp = _currentTimestamp();
    setState(() {
      _messages.add(
        _AiChatMessageData(
          sender: _AiChatSender.user,
          text: text,
          senderLabel: 'Sen',
          timestamp: timestamp,
        ),
      );
      _composerController.clear();
    });
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!_scrollController.hasClients) {
        return;
      }
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent + 160,
        duration: const Duration(milliseconds: 220),
        curve: Curves.easeOutCubic,
      );
    });
  }

  String _currentTimestamp() {
    final now = DateTime.now();
    final hour = now.hour.toString().padLeft(2, '0');
    final minute = now.minute.toString().padLeft(2, '0');
    return '$hour:$minute';
  }

  @override
  Widget build(BuildContext context) {
    final palette = _AiReferencePalette.of(context);

    return Scaffold(
      backgroundColor: palette.canvas,
      body: DecoratedBox(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [palette.canvas, palette.canvas, palette.lowerGlow],
            stops: const [0, 0.68, 1],
          ),
        ),
        child: SafeArea(
          bottom: false,
          child: Column(
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(20, 12, 20, 0),
                child: JoviaReveal(child: _AiChatHeader(onMoreTap: () {})),
              ),
              const SizedBox(height: 8),
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: JoviaReveal(
                    delay: const Duration(milliseconds: 30),
                    child: _AiChatShell(
                      messages: _messages,
                      scrollController: _scrollController,
                    ),
                  ),
                ),
              ),
              SafeArea(
                top: false,
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(20, 10, 20, 12),
                  child: JoviaReveal(
                    delay: const Duration(milliseconds: 50),
                    child: _AiChatDock(
                      controller: _composerController,
                      onSend: _sendDraft,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

enum _AiChatSender { aila, user }

class _AiChatMessageData {
  const _AiChatMessageData({
    required this.sender,
    required this.text,
    required this.senderLabel,
    required this.timestamp,
  });

  final _AiChatSender sender;
  final String text;
  final String senderLabel;
  final String timestamp;
}

class _AiReferencePalette {
  const _AiReferencePalette({
    required this.canvas,
    required this.lowerGlow,
    required this.surface,
    required this.softFill,
    required this.edge,
    required this.rule,
    required this.text,
    required this.mutedText,
    required this.softText,
    required this.userFill,
    required this.assistantFill,
  });

  final Color canvas;
  final Color lowerGlow;
  final Color surface;
  final Color softFill;
  final Color edge;
  final Color rule;
  final Color text;
  final Color mutedText;
  final Color softText;
  final Color userFill;
  final Color assistantFill;

  static _AiReferencePalette of(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return isDark
        ? const _AiReferencePalette(
            canvas: Color(0xFF070708),
            lowerGlow: Color(0xFF141112),
            surface: Color(0xFF0E0C0D),
            softFill: Color(0xFF181415),
            edge: Color(0xFFB97B46),
            rule: Color(0xFF4B3B33),
            text: Color(0xFFF5F1EB),
            mutedText: Color(0xFFC7BCB1),
            softText: Color(0xFFB2A69B),
            userFill: Color(0xFF1F1815),
            assistantFill: Color(0xFF131113),
          )
        : const _AiReferencePalette(
            canvas: Color(0xFFF5F0E8),
            lowerGlow: Color(0xFFECE0D4),
            surface: Color(0xFFFBF6EF),
            softFill: Color(0xFFF2E7D9),
            edge: Color(0xFFD6945A),
            rule: Color(0xFF7F6A59),
            text: Color(0xFF171211),
            mutedText: Color(0xFF6F6257),
            softText: Color(0xFF9B8677),
            userFill: Color(0xFFF3E9DE),
            assistantFill: Color(0xFFFFFBF6),
          );
  }
}

class _AiChatShell extends StatelessWidget {
  const _AiChatShell({required this.messages, required this.scrollController});

  final List<_AiChatMessageData> messages;
  final ScrollController scrollController;

  @override
  Widget build(BuildContext context) {
    final palette = _AiReferencePalette.of(context);
    return Stack(
      children: [
        Positioned.fill(
          child: Opacity(
            opacity: Theme.of(context).brightness == Brightness.dark
                ? 0.12
                : 0.08,
            child: const JoviaColorWash(
              asset: JoviaColorAsset.wash09,
              fit: BoxFit.cover,
            ),
          ),
        ),
        if (messages.isEmpty)
          const _AiEmptyState()
        else
          ListView.separated(
            controller: scrollController,
            padding: const EdgeInsets.fromLTRB(0, 12, 0, 18),
            itemCount: messages.length,
            separatorBuilder: (_, _) => const SizedBox(height: 14),
            itemBuilder: (context, index) {
              return _AiMessageBubble(message: messages[index]);
            },
          ),
        Positioned(
          left: 0,
          right: 0,
          bottom: 0,
          child: IgnorePointer(
            child: Container(
              height: 28,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    palette.canvas.withValues(alpha: 0),
                    palette.canvas.withValues(alpha: 0.92),
                  ],
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

class _AiEmptyState extends StatelessWidget {
  const _AiEmptyState();

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final palette = _AiReferencePalette.of(context);
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 320),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 72,
              height: 72,
              decoration: BoxDecoration(
                color: palette.softFill.withValues(alpha: 0.82),
                borderRadius: BorderRadius.circular(24),
                border: Border.all(color: palette.rule.withValues(alpha: 0.56)),
              ),
              child: Center(
                child: JoviaUiIcon(
                  asset: JoviaUiAsset.chatOrbit,
                  size: 28,
                  color: palette.softText,
                ),
              ),
            ),
            const SizedBox(height: 18),
            Text(
              'Mesajını yaz ve konuşmayı başlat.',
              textAlign: TextAlign.center,
              style: profile.typography.cardTitle.copyWith(color: palette.text),
            ),
            const SizedBox(height: 8),
            Text(
              'Bu alan backend bağlandığında doğal bir konuşma akışıyla dolacak.',
              textAlign: TextAlign.center,
              style: profile.typography.bodyCompact.copyWith(
                color: palette.mutedText,
                height: 1.56,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _AiMessageBubble extends StatelessWidget {
  const _AiMessageBubble({required this.message});

  final _AiChatMessageData message;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final palette = _AiReferencePalette.of(context);
    final isAila = message.sender == _AiChatSender.aila;
    final maxWidth = MediaQuery.sizeOf(context).width * (isAila ? 0.78 : 0.72);
    return Column(
      crossAxisAlignment: isAila
          ? CrossAxisAlignment.start
          : CrossAxisAlignment.end,
      children: [
        Align(
          alignment: isAila ? Alignment.centerLeft : Alignment.centerRight,
          child: ConstrainedBox(
            constraints: BoxConstraints(maxWidth: maxWidth.clamp(248.0, 360.0)),
            child: Container(
              padding: const EdgeInsets.fromLTRB(16, 14, 16, 14),
              decoration: BoxDecoration(
                color: isAila ? palette.assistantFill : palette.userFill,
                borderRadius: BorderRadius.only(
                  topLeft: const Radius.circular(20),
                  topRight: const Radius.circular(20),
                  bottomLeft: Radius.circular(isAila ? 6 : 20),
                  bottomRight: Radius.circular(isAila ? 20 : 6),
                ),
                border: Border.all(
                  color: (isAila ? palette.rule : palette.edge).withValues(
                    alpha: 0.55,
                  ),
                ),
              ),
              child: Text(
                message.text,
                style: profile.typography.bodyCompact.copyWith(
                  color: palette.text,
                  height: 1.56,
                ),
              ),
            ),
          ),
        ),
        const SizedBox(height: 6),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 4),
          child: Text(
            '${message.senderLabel}  ${message.timestamp}',
            style: profile.typography.meta.copyWith(color: palette.softText),
          ),
        ),
      ],
    );
  }
}

class _AiChatHeader extends StatelessWidget {
  const _AiChatHeader({required this.onMoreTap});

  final VoidCallback onMoreTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final palette = _AiReferencePalette.of(context);
    return SizedBox(
      height: 56,
      child: Row(
        children: [
          const SizedBox(width: 44),
          Expanded(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  'Aila',
                  style: profile.typography.cardTitle.copyWith(
                    color: palette.text,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  'Online',
                  style: profile.typography.meta.copyWith(
                    color: palette.softText,
                  ),
                ),
              ],
            ),
          ),
          JoviaPressable(
            onTap: onMoreTap,
            borderRadius: BorderRadius.circular(999),
            child: SizedBox(
              width: 44,
              height: 44,
              child: Center(
                child: JoviaUiIcon(
                  asset: JoviaUiAsset.menuStack,
                  size: 18,
                  color: palette.text,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _AiChatDock extends StatelessWidget {
  const _AiChatDock({required this.controller, required this.onSend});

  final TextEditingController controller;
  final VoidCallback onSend;

  @override
  Widget build(BuildContext context) {
    final palette = _AiReferencePalette.of(context);
    return DecoratedBox(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            palette.canvas.withValues(alpha: 0.18),
            palette.canvas.withValues(alpha: 0.94),
          ],
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.only(top: 8),
        child: _AiComposer(controller: controller, onSend: onSend),
      ),
    );
  }
}

class _AiComposer extends StatelessWidget {
  const _AiComposer({required this.controller, required this.onSend});

  final TextEditingController controller;
  final VoidCallback onSend;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final palette = _AiReferencePalette.of(context);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
      decoration: BoxDecoration(
        color: palette.surface.withValues(alpha: 0.94),
        borderRadius: BorderRadius.circular(28),
        border: Border.all(
          color: palette.edge.withValues(alpha: 0.82),
          width: 1.2,
        ),
      ),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: controller,
              minLines: 1,
              maxLines: 4,
              style: profile.typography.bodyCompact.copyWith(
                color: palette.text,
              ),
              decoration: InputDecoration(
                hintText: "Aila'ya yaz...",
                hintStyle: profile.typography.bodyCompact.copyWith(
                  color: palette.softText,
                ),
                isCollapsed: true,
                border: InputBorder.none,
              ),
            ),
          ),
          const SizedBox(width: 14),
          JoviaPressable(
            onTap: onSend,
            borderRadius: BorderRadius.circular(999),
            child: Container(
              width: 42,
              height: 42,
              decoration: BoxDecoration(
                color: palette.softFill,
                borderRadius: BorderRadius.circular(999),
                border: Border.all(color: palette.edge.withValues(alpha: 0.56)),
              ),
              child: Center(
                child: JoviaUiIcon(
                  asset: JoviaUiAsset.chevronRight,
                  size: 18,
                  color: palette.text,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
