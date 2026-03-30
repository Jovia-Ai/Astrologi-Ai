import 'package:flutter/material.dart';

class ForumComposeBar extends StatelessWidget {
  const ForumComposeBar({super.key, required this.label, required this.onTap});

  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      top: false,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 12),
        child: Material(
          color: const Color(0xFF121212),
          borderRadius: BorderRadius.circular(20),
          child: InkWell(
            onTap: onTap,
            borderRadius: BorderRadius.circular(20),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: const Color(0xFF222222)),
              ),
              child: Row(
                children: [
                  const Icon(
                    Icons.edit_outlined,
                    size: 18,
                    color: Color(0xFF7C7C7C),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      label,
                      style: const TextStyle(
                        fontSize: 13,
                        color: Color(0xFF7C7C7C),
                      ),
                    ),
                  ),
                  const Icon(
                    Icons.arrow_upward_rounded,
                    size: 18,
                    color: Color(0xFFA0A0A0),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
