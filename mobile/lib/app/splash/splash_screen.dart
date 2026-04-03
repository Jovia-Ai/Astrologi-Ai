import 'package:flutter/material.dart';
import 'package:mobile/design/widgets/jovia_assets.dart';

const Duration kSplashMotionDuration = Duration(milliseconds: 920);
const Duration kSplashFadeDuration = Duration(milliseconds: 220);
const double kSplashLogoWidthFactor = 0.7;
const double kSplashLogoMinWidth = 220;
const double kSplashLogoMaxWidth = 420;
const double kSplashInitialScale = 0.92;
const double kSplashPeakScale = 1.02;
const double kSplashInitialOffsetY = 16;
const Color kSplashBackgroundColor = Color(0xFF000000);

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key, required this.child});

  final Widget child;

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen>
    with TickerProviderStateMixin {
  late final AnimationController _motionController;
  late final AnimationController _fadeController;
  late final Animation<double> _logoOpacity;
  late final Animation<double> _logoScale;
  late final Animation<double> _logoOffsetY;
  late final Animation<double> _splashOpacity;
  late final Animation<double> _childOpacity;

  bool _showChild = false;

  @override
  void initState() {
    super.initState();
    _motionController = AnimationController(
      vsync: this,
      duration: kSplashMotionDuration,
    );
    _fadeController = AnimationController(
      vsync: this,
      duration: kSplashFadeDuration,
    );

    _logoOpacity = CurvedAnimation(
      parent: _motionController,
      curve: const Interval(0.0, 0.26, curve: Curves.easeOutCubic),
    );
    _logoScale = TweenSequence<double>([
      TweenSequenceItem<double>(
        tween: Tween<double>(
          begin: kSplashInitialScale,
          end: 1.0,
        ).chain(CurveTween(curve: Curves.easeOutCubic)),
        weight: 68,
      ),
      TweenSequenceItem<double>(
        tween: Tween<double>(
          begin: 1.0,
          end: kSplashPeakScale,
        ).chain(CurveTween(curve: Curves.easeOut)),
        weight: 8,
      ),
      TweenSequenceItem<double>(
        tween: Tween<double>(
          begin: kSplashPeakScale,
          end: 1.0,
        ).chain(CurveTween(curve: Curves.easeInOutCubic)),
        weight: 10,
      ),
      TweenSequenceItem<double>(tween: ConstantTween<double>(1.0), weight: 14),
    ]).animate(_motionController);
    _logoOffsetY = Tween<double>(begin: kSplashInitialOffsetY, end: 0).animate(
      CurvedAnimation(
        parent: _motionController,
        curve: const Interval(0.0, 0.3, curve: Curves.easeOutCubic),
      ),
    );
    _splashOpacity = Tween<double>(begin: 1.0, end: 0.0).animate(
      CurvedAnimation(parent: _fadeController, curve: Curves.easeInOutCubic),
    );
    _childOpacity = CurvedAnimation(
      parent: _fadeController,
      curve: Curves.easeInOutCubic,
    );

    _motionController.addStatusListener((status) {
      if (status != AnimationStatus.completed || !mounted) {
        return;
      }
      setState(() => _showChild = true);
      _fadeController.forward();
    });

    _motionController.forward();
  }

  @override
  void dispose() {
    _motionController.dispose();
    _fadeController.dispose();
    super.dispose();
  }

  double _logoWidth(BuildContext context) {
    final width = MediaQuery.of(context).size.width * kSplashLogoWidthFactor;
    return width.clamp(kSplashLogoMinWidth, kSplashLogoMaxWidth).toDouble();
  }

  Widget _buildSplash(BuildContext context) {
    return ColoredBox(
      color: kSplashBackgroundColor,
      child: Center(
        child: FadeTransition(
          opacity: _logoOpacity,
          child: AnimatedBuilder(
            animation: _motionController,
            child: _SplashLogo(width: _logoWidth(context)),
            builder: (context, child) {
              return Transform.translate(
                offset: Offset(0, _logoOffsetY.value),
                child: Transform.scale(scale: _logoScale.value, child: child),
              );
            },
          ),
        ),
      ),
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

class _SplashLogo extends StatelessWidget {
  const _SplashLogo({required this.width});

  final double width;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      constraints: const BoxConstraints(maxWidth: kSplashLogoMaxWidth),
      decoration: const BoxDecoration(
        boxShadow: [
          BoxShadow(color: Color.fromRGBO(255, 255, 255, 0.05), blurRadius: 30),
        ],
      ),
      child: JoviaBrandMark(
        width: width,
        alignment: Alignment.center,
        opacity: 1,
        color: Colors.white,
      ),
    );
  }
}
