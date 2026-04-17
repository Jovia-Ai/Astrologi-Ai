import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:mobile/app/telemetry/perf_telemetry.dart';

const Duration kSplashMotionDuration = Duration(milliseconds: 2200);
const Duration kSplashIdlePulseDuration = Duration(milliseconds: 3200);
const Duration kSplashFadeDuration = Duration(milliseconds: 220);
const double kSplashBackgroundColorAlpha = 1.0;
const Color kSplashBackgroundColor = Color(0xFF111111);
const Color kSplashLime = Color(0xFFCAFF4D);

const Cubic _kSplashStandardEase = Cubic(0.4, 0.0, 0.2, 1.0);
const Cubic _kSplashBackEase = Cubic(0.34, 1.56, 0.64, 1.0);

class SplashScreen extends StatefulWidget {
  const SplashScreen({
    super.key,
    required this.child,
    this.readyToReveal = true,
  });

  final Widget child;
  final bool readyToReveal;

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen>
    with TickerProviderStateMixin {
  late final AnimationController _motionController;
  late final AnimationController _idleController;
  late final AnimationController _fadeController;
  late final Animation<double> _splashOpacity;
  late final Animation<double> _childOpacity;

  bool _showChild = false;

  @override
  void initState() {
    super.initState();
    PerfTelemetry.logPointOnce('startup.splash_visible', 'splash_visible');
    _motionController = AnimationController(
      vsync: this,
      duration: kSplashMotionDuration,
    );
    _idleController = AnimationController(
      vsync: this,
      duration: kSplashIdlePulseDuration,
    );
    _fadeController = AnimationController(
      vsync: this,
      duration: kSplashFadeDuration,
    );

    _splashOpacity = Tween<double>(begin: 1.0, end: 0.0).animate(
      CurvedAnimation(parent: _fadeController, curve: Curves.easeInOutCubic),
    );
    _childOpacity = CurvedAnimation(
      parent: _fadeController,
      curve: Curves.easeInOutCubic,
    );

    _motionController.addStatusListener((status) {
      if (status != AnimationStatus.completed) {
        return;
      }
      if (!_idleController.isAnimating) {
        _idleController.repeat();
      }
      if (widget.readyToReveal) {
        _revealChild();
      }
    });

    _motionController.forward();
  }

  @override
  void didUpdateWidget(covariant SplashScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (!oldWidget.readyToReveal && widget.readyToReveal) {
      if (_motionController.status == AnimationStatus.completed) {
        if (!_idleController.isAnimating) {
          _idleController.repeat();
        }
        _revealChild();
      }
    }
  }

  void _revealChild() {
    if (!mounted || _showChild) {
      return;
    }
    setState(() => _showChild = true);
    if (!_fadeController.isAnimating && !_fadeController.isCompleted) {
      _fadeController.forward();
    }
  }

  @override
  void dispose() {
    _motionController.dispose();
    _idleController.dispose();
    _fadeController.dispose();
    super.dispose();
  }

  double _interval(
    double t,
    double start,
    double end, {
    Curve curve = Curves.linear,
  }) {
    return _intervalRaw(t, start, end, curve: curve).clamp(0.0, 1.0);
  }

  double _intervalRaw(
    double t,
    double start,
    double end, {
    Curve curve = Curves.linear,
  }) {
    if (t <= start) {
      return 0;
    }
    if (t >= end) {
      return 1;
    }
    final normalized = (t - start) / (end - start);
    return curve.transform(normalized.clamp(0.0, 1.0));
  }

  double _loadingProgress(double t) {
    final elapsedMs = t * kSplashMotionDuration.inMilliseconds;
    final p = ((elapsedMs - 800.0) / 2200.0).clamp(0.0, 1.0).toDouble();
    if (p <= 0.2) {
      return _lerp(0.0, 0.12, p / 0.2);
    }
    if (p <= 0.5) {
      return _lerp(0.12, 0.45, (p - 0.2) / 0.3);
    }
    if (p <= 0.8) {
      return _lerp(0.45, 0.78, (p - 0.5) / 0.3);
    }
    return _lerp(0.78, 1.0, (p - 0.8) / 0.2);
  }

  double _atMs(double ms) {
    return (ms / kSplashMotionDuration.inMilliseconds).clamp(0.0, 1.0);
  }

  double _logoWidth(BuildContext context) {
    final width = MediaQuery.of(context).size.width * 0.2667;
    return width.clamp(98.0, 126.0).toDouble();
  }

  Widget _buildSplash(BuildContext context) {
    return AnimatedBuilder(
      animation: Listenable.merge([_motionController, _idleController]),
      builder: (context, _) {
        final t = _motionController.value;
        final idleT = _idleController.value;

        final logoReveal = _interval(
          t,
          _atMs(100),
          _atMs(700),
          curve: _kSplashStandardEase,
        );
        final outerProgress = _interval(
          t,
          _atMs(200),
          _atMs(1600),
          curve: _kSplashStandardEase,
        );
        final innerProgress = _interval(
          t,
          _atMs(550),
          _atMs(1650),
          curve: _kSplashStandardEase,
        );
        final centerPop = _interval(
          t,
          _atMs(850),
          _atMs(1350),
          curve: _kSplashBackEase,
        );
        final centerDotScale = _centerDotKeyframeScale(centerPop);
        final topDrop = _intervalRaw(
          t,
          _atMs(1000),
          _atMs(1500),
          curve: _kSplashBackEase,
        );
        final lineGrow = _interval(
          t,
          _atMs(1100),
          _atMs(1500),
          curve: _kSplashStandardEase,
        );

        final wordmarkTitle = _interval(
          t,
          _atMs(900),
          _atMs(1600),
          curve: Curves.ease,
        );
        final wordmarkSub = _interval(
          t,
          _atMs(1050),
          _atMs(1750),
          curve: Curves.ease,
        );
        final tagline = _interval(
          t,
          _atMs(1300),
          _atMs(2100),
          curve: Curves.ease,
        );
        final loading = _loadingProgress(t);
        final loadingVisibility = _interval(
          t,
          _atMs(1000),
          _atMs(1500),
          curve: Curves.ease,
        );
        final glowOpacity = _interval(
          t,
          _atMs(400),
          _atMs(2200),
          curve: Curves.easeOut,
        );

        final breathe = 1 + 0.015 * math.sin(idleT * 2 * math.pi);
        final centerPulseScale =
            1 + 3.5 * (0.5 + 0.5 * math.sin(idleT * 2 * math.pi));
        final centerPulseOpacity =
            0.3 * (0.5 + 0.5 * math.sin(idleT * 2 * math.pi));
        final topPulseScale =
            1 + 1.4 * (0.5 + 0.5 * math.sin(idleT * 2 * math.pi + 1.1));
        final topPulseOpacity =
            0.25 * (0.5 + 0.5 * math.sin(idleT * 2 * math.pi + 1.1));

        final logoScale = _lerp(0.88, 1.0, logoReveal) * breathe;
        final logoOffsetY = _lerp(12, 0, logoReveal);

        return Material(
          color: kSplashBackgroundColor.withValues(
            alpha: kSplashBackgroundColorAlpha,
          ),
          child: Stack(
            fit: StackFit.expand,
            children: [
              _SplashAmbientBackground(opacity: glowOpacity),
              Center(
                child: Transform.translate(
                  offset: Offset(0, logoOffsetY),
                  child: Transform.scale(
                    scale: logoScale,
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        _SplashOrbitLogo(
                          size: _logoWidth(context),
                          outerProgress: outerProgress,
                          innerProgress: innerProgress,
                          centerDotScale: centerDotScale,
                          topDotProgress: topDrop,
                          lineProgress: lineGrow,
                          centerPulseScale: centerPulseScale,
                          centerPulseOpacity: centerPulseOpacity,
                          topPulseScale: topPulseScale,
                          topPulseOpacity: topPulseOpacity,
                        ),
                        const SizedBox(height: 20),
                        Transform.translate(
                          offset: Offset(0, _lerp(10, 0, wordmarkTitle)),
                          child: Opacity(
                            opacity: wordmarkTitle,
                            child: const Text(
                              'SHOU',
                              style: TextStyle(
                                fontSize: 28,
                                color: Colors.white,
                                letterSpacing: 3.9,
                                fontWeight: FontWeight.w400,
                                decoration: TextDecoration.none,
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(height: 4),
                        Transform.translate(
                          offset: Offset(0, _lerp(10, 0, wordmarkSub)),
                          child: Opacity(
                            opacity: wordmarkSub,
                            child: const Text(
                              'ASTROLOGI AI',
                              style: TextStyle(
                                fontSize: 9.3,
                                color: Color(0xFF888888),
                                letterSpacing: 1.9,
                                fontWeight: FontWeight.w400,
                                decoration: TextDecoration.none,
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(height: 36),
                        Opacity(
                          opacity: tagline,
                          child: const Text(
                            'Gökyüzü seni bekliyor.',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              fontSize: 13,
                              color: Color(0xFF9A9A9A),
                              letterSpacing: 0.65,
                              height: 1.7,
                              fontWeight: FontWeight.w400,
                              decoration: TextDecoration.none,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
              Positioned(
                left: 0,
                right: 0,
                bottom: 56,
                child: Opacity(
                  opacity: loadingVisibility,
                  child: Center(
                    child: SizedBox(
                      width: 48,
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Container(
                            height: 1.5,
                            width: 48,
                            decoration: BoxDecoration(
                              color: Colors.white.withValues(alpha: 0.12),
                              borderRadius: BorderRadius.circular(1),
                            ),
                            alignment: Alignment.centerLeft,
                            child: FractionallySizedBox(
                              widthFactor: loading,
                              alignment: Alignment.centerLeft,
                              child: Container(
                                decoration: BoxDecoration(
                                  color: kSplashLime,
                                  borderRadius: BorderRadius.circular(1),
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final splash = _buildSplash(context);
    if (!_showChild) {
      return splash;
    }
    return Stack(
      fit: StackFit.expand,
      children: [
        FadeTransition(opacity: _childOpacity, child: widget.child),
        AnimatedBuilder(
          animation: _fadeController,
          child: splash,
          builder: (context, child) => IgnorePointer(
            ignoring: _fadeController.isCompleted,
            child: FadeTransition(opacity: _splashOpacity, child: child),
          ),
        ),
      ],
    );
  }
}

class _SplashAmbientBackground extends StatelessWidget {
  const _SplashAmbientBackground({required this.opacity});

  final double opacity;

  @override
  Widget build(BuildContext context) {
    return Opacity(
      opacity: opacity,
      child: Stack(
        fit: StackFit.expand,
        children: [
          Positioned.fill(child: CustomPaint(painter: _AmbientOrbitPainter())),
          Align(
            alignment: const Alignment(0, -0.16),
            child: _GlowBlob(
              width: 360,
              height: 320,
              color: kSplashLime.withValues(alpha: 0.06),
            ),
          ),
          Align(
            alignment: const Alignment(0.55, 0.22),
            child: _GlowBlob(
              width: 270,
              height: 220,
              color: const Color(0xFF7F77DD).withValues(alpha: 0.08),
            ),
          ),
          Align(
            alignment: const Alignment(-0.55, 0.32),
            child: _GlowBlob(
              width: 220,
              height: 190,
              color: const Color(0xFFF9A8D4).withValues(alpha: 0.06),
            ),
          ),
        ],
      ),
    );
  }
}

class _GlowBlob extends StatelessWidget {
  const _GlowBlob({
    required this.width,
    required this.height,
    required this.color,
  });

  final double width;
  final double height;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: width,
      height: height,
      child: DecoratedBox(
        decoration: BoxDecoration(
          shape: BoxShape.rectangle,
          borderRadius: BorderRadius.circular(width),
          gradient: RadialGradient(colors: [color, color.withValues(alpha: 0)]),
        ),
      ),
    );
  }
}

class _SplashOrbitLogo extends StatelessWidget {
  const _SplashOrbitLogo({
    required this.size,
    required this.outerProgress,
    required this.innerProgress,
    required this.centerDotScale,
    required this.topDotProgress,
    required this.lineProgress,
    required this.centerPulseScale,
    required this.centerPulseOpacity,
    required this.topPulseScale,
    required this.topPulseOpacity,
  });

  final double size;
  final double outerProgress;
  final double innerProgress;
  final double centerDotScale;
  final double topDotProgress;
  final double lineProgress;
  final double centerPulseScale;
  final double centerPulseOpacity;
  final double topPulseScale;
  final double topPulseOpacity;

  @override
  Widget build(BuildContext context) {
    final centerDotSize = size * 0.08;
    final topDotSize = size * 0.1;
    final lineHeight = size * 0.15;
    final lineWidth = 1.2;
    final topDropY = _lerp(-12, 0, topDotProgress);
    final topDotOpacity = topDotProgress.clamp(0.0, 1.0).toDouble();

    return SizedBox(
      width: size,
      height: size,
      child: Stack(
        clipBehavior: Clip.none,
        children: [
          Positioned.fill(
            child: CustomPaint(
              painter: _OrbitRingsPainter(
                outerProgress: outerProgress,
                innerProgress: innerProgress,
              ),
            ),
          ),
          Align(
            alignment: Alignment.center,
            child: Opacity(
              opacity: centerPulseOpacity,
              child: Transform.scale(
                scale: centerPulseScale,
                child: Container(
                  width: centerDotSize,
                  height: centerDotSize,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: kSplashLime.withValues(alpha: 0.9),
                      width: 0.8,
                    ),
                  ),
                ),
              ),
            ),
          ),
          Positioned(
            left: size * 0.5 - topDotSize * 0.5,
            top: size * 0.08,
            child: Opacity(
              opacity: topPulseOpacity,
              child: Transform.scale(
                scale: topPulseScale,
                child: Container(
                  width: topDotSize,
                  height: topDotSize,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: kSplashLime.withValues(alpha: 0.85),
                      width: 0.8,
                    ),
                  ),
                ),
              ),
            ),
          ),
          Positioned(
            left: size * 0.5 - lineWidth / 2,
            top: size * 0.13,
            child: Opacity(
              opacity: lineProgress,
              child: Transform.scale(
                scaleY: lineProgress,
                alignment: Alignment.bottomCenter,
                child: Container(
                  width: lineWidth,
                  height: lineHeight,
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(10),
                  ),
                ),
              ),
            ),
          ),
          Align(
            alignment: Alignment.center,
            child: Transform.scale(
              scale: centerDotScale,
              child: Container(
                width: centerDotSize,
                height: centerDotSize,
                decoration: const BoxDecoration(
                  color: kSplashLime,
                  shape: BoxShape.circle,
                ),
              ),
            ),
          ),
          Positioned(
            left: size * 0.5 - topDotSize * 0.5,
            top: size * 0.08,
            child: Transform.translate(
              offset: Offset(0, topDropY),
              child: Opacity(
                opacity: topDotOpacity,
                child: Container(
                  width: topDotSize,
                  height: topDotSize,
                  decoration: const BoxDecoration(
                    color: kSplashLime,
                    shape: BoxShape.circle,
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _OrbitRingsPainter extends CustomPainter {
  const _OrbitRingsPainter({
    required this.outerProgress,
    required this.innerProgress,
  });

  final double outerProgress;
  final double innerProgress;

  @override
  void paint(Canvas canvas, Size size) {
    final stroke = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.5
      ..color = Colors.white;

    final center = Offset(size.width / 2, size.height / 2);
    final outerRect = Rect.fromCircle(
      center: center,
      radius: size.width * 0.42,
    );
    final innerRect = Rect.fromCircle(
      center: center,
      radius: size.width * 0.22,
    );

    if (outerProgress > 0) {
      canvas.drawArc(
        outerRect,
        -math.pi / 2,
        (2 * math.pi) * outerProgress,
        false,
        stroke,
      );
    }

    if (innerProgress > 0) {
      canvas.drawArc(
        innerRect,
        -math.pi / 2,
        (2 * math.pi) * innerProgress,
        false,
        stroke,
      );
    }
  }

  @override
  bool shouldRepaint(covariant _OrbitRingsPainter oldDelegate) {
    return oldDelegate.outerProgress != outerProgress ||
        oldDelegate.innerProgress != innerProgress;
  }
}

class _AmbientOrbitPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height * 0.42);
    final ring1 = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 0.8
      ..color = Colors.white.withValues(alpha: 0.014);
    final ring2 = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 0.8
      ..color = Colors.white.withValues(alpha: 0.010);

    _drawDashedCircle(canvas, center, size.shortestSide * 0.36, ring1, 3, 10);
    _drawDashedCircle(canvas, center, size.shortestSide * 0.5, ring2, 2, 8);
  }

  void _drawDashedCircle(
    Canvas canvas,
    Offset center,
    double radius,
    Paint paint,
    double dashLength,
    double gapLength,
  ) {
    final circumference = 2 * math.pi * radius;
    final segmentLength = dashLength + gapLength;
    final count = (circumference / segmentLength).floor();
    final rect = Rect.fromCircle(center: center, radius: radius);
    for (var i = 0; i < count; i++) {
      final start = (i * segmentLength / circumference) * 2 * math.pi;
      final sweep = (dashLength / circumference) * 2 * math.pi;
      canvas.drawArc(rect, start, sweep, false, paint);
    }
  }

  @override
  bool shouldRepaint(covariant _AmbientOrbitPainter oldDelegate) => false;
}

double _lerp(double begin, double end, double t) {
  return begin + (end - begin) * t.clamp(0.0, 1.0);
}

double _centerDotKeyframeScale(double t) {
  final p = t.clamp(0.0, 1.0).toDouble();
  if (p <= 0.0) {
    return 0.0;
  }
  if (p <= 0.6) {
    return _lerp(0.0, 1.3, p / 0.6);
  }
  return _lerp(1.3, 1.0, (p - 0.6) / 0.4);
}
