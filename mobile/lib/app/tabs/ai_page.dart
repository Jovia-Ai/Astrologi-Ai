import 'package:flutter/material.dart';

import 'package:mobile/design/theme/profile_theme_extension.dart';
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

  List<_AiChatMessageData> get _conversationMessages {
    if (_messages.isNotEmpty) {
      return _messages;
    }
    return const <_AiChatMessageData>[
      _AiChatMessageData(
        sender: _AiChatSender.aila,
        text:
            'Merhaba, ben Aila. İstersen bugün hissettiğin şeyi, aklındaki bir konuyu ya da haritana dair merak ettiğin bir detayı yaz.',
        senderLabel: 'Aila',
        timestamp: 'Şimdi',
      ),
    ];
  }

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
    final profile = context.profileTheme;
    final palette = _AiReferencePalette.of(context);
    final messages = _conversationMessages;

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
                child: JoviaReveal(child: _AiTopBar(onMoreTap: () {})),
              ),
              SizedBox(height: profile.spacing.s12),
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: JoviaReveal(
                    delay: const Duration(milliseconds: 30),
                    child: _AiChatShell(
                      messages: messages,
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
    final colors = context.profileTheme.colors;
    return _AiReferencePalette(
      canvas: colors.bg,
      lowerGlow: Color.alphaBlend(
        colors.neonPink.withValues(alpha: 0.12),
        colors.bg,
      ),
      surface: colors.panelStrong,
      softFill: colors.panelSoft,
      edge: colors.warmAccent.withValues(alpha: 0.72),
      rule: colors.strokeSoft.withValues(alpha: 0.92),
      text: colors.text,
      mutedText: colors.muted,
      softText: colors.textLight,
      userFill: Color.alphaBlend(
        colors.warmAccent.withValues(alpha: 0.1),
        colors.panelStrong,
      ),
      assistantFill: Color.alphaBlend(
        colors.primary.withValues(alpha: 0.08),
        colors.panelStrong,
      ),
    );
  }
}

class _AiTopBar extends StatelessWidget {
  const _AiTopBar({required this.onMoreTap});

  final VoidCallback onMoreTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final palette = _AiReferencePalette.of(context);
    return Row(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            color: palette.softFill.withValues(alpha: 0.92),
            shape: BoxShape.circle,
            border: Border.all(color: palette.rule),
          ),
          child: Center(
            child: JoviaUiIcon(
              asset: JoviaUiAsset.chatOrbit,
              size: 20,
              color: palette.text,
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Aila',
                style: profile.typography.cardTitle.copyWith(
                  color: palette.text,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                'Çevrimiçi',
                style: profile.typography.meta.copyWith(
                  color: palette.softText,
                ),
              ),
            ],
          ),
        ),
        JoviaGlassIconButton(
          onTap: onMoreTap,
          size: 46,
          child: JoviaUiIcon(
            asset: JoviaUiAsset.menuStack,
            size: 18,
            color: palette.text,
          ),
        ),
      ],
    );
  }
}

class _AiChatShell extends StatelessWidget {
  const _AiChatShell({required this.messages, required this.scrollController});

  final List<_AiChatMessageData> messages;
  final ScrollController scrollController;

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      controller: scrollController,
      padding: const EdgeInsets.fromLTRB(0, 12, 0, 20),
      itemCount: messages.length,
      separatorBuilder: (_, _) => const SizedBox(height: 14),
      itemBuilder: (context, index) {
        return _AiMessageBubble(message: messages[index]);
      },
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
        border: Border.all(color: palette.rule, width: 1.2),
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
                color: palette.userFill,
                borderRadius: BorderRadius.circular(999),
                border: Border.all(color: palette.edge.withValues(alpha: 0.5)),
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
