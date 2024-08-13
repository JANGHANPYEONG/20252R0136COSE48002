import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:structure/config/palette.dart';

class CustomDropdown extends StatefulWidget {
  final Widget hintText;
  final String? value;
  final List<String> itemList;
  final bool hasDropdown;
  final Function(String?, int)? onChanged;

  const CustomDropdown({
    super.key,
    required this.hintText,
    required this.value,
    required this.itemList,
    required this.onChanged,
    this.hasDropdown = true,
  });

  @override
  State<CustomDropdown> createState() => _CustomDropdownState();
}

class _CustomDropdownState extends State<CustomDropdown> {
  final LayerLink _layerLink = LayerLink();
  final ScrollController scrollController = ScrollController();
  final FocusNode _focusNode = FocusNode();
  OverlayEntry? _overlayEntry;

  @override
  void initState() {
    super.initState();
    _focusNode.addListener(() {
      if (!_focusNode.hasFocus) {
        _removeDropdown();
      }
    });
  }

  void _toggleDropdown() {
    if (widget.itemList.isNotEmpty) {
      if (_overlayEntry == null) {
        _focusNode.requestFocus(); // 포커스를 요청
        _overlayEntry = _createOverlayEntry();
        Overlay.of(context).insert(_overlayEntry!);
      } else {
        _removeDropdown();
      }
    }
  }

  void _removeDropdown() {
    _overlayEntry?.remove();
    _overlayEntry = null;
    _focusNode.unfocus();
  }

  OverlayEntry _createOverlayEntry() {
    RenderBox renderBox = context.findRenderObject() as RenderBox;
    Size size = renderBox.size;
    return OverlayEntry(
      builder: (context) => Positioned(
        width: size.width,
        child: CompositedTransformFollower(
          link: _layerLink,
          showWhenUnlinked: false,
          offset: Offset(0, size.height + 16.h),
          child: Material(
            elevation: 0.0,
            child: Container(
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(20.r),
                border: Border.all(
                  color: Palette.primary,
                ),
              ),
              constraints: BoxConstraints(maxHeight: 400.h),
              child: Scrollbar(
                thumbVisibility: true,
                controller: scrollController,
                child: ListView.builder(
                  controller: scrollController,
                  padding: EdgeInsets.zero,
                  shrinkWrap: true,
                  physics: const ClampingScrollPhysics(),
                  itemCount: widget.itemList.length,
                  itemBuilder: (context, index) {
                    String item = widget.itemList[index];
                    return ListTile(
                      title: Text(item, style: Palette.h4),
                      onTap: () {
                        widget.onChanged!(item, index);
                        _removeDropdown();
                      },
                    );
                  },
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return CompositedTransformTarget(
      link: _layerLink,
      child: GestureDetector(
        onTap: _toggleDropdown,
        child: Focus(
          focusNode: _focusNode,
          child: Container(
            decoration: BoxDecoration(
              color: Palette.onPrimaryContainer,
              borderRadius: BorderRadius.circular(20.r),
              border: Border.all(
                color: widget.value != null
                    ? Palette.primary
                    : Palette.onPrimaryContainer,
                width: 1.0,
              ),
            ),
            padding: EdgeInsets.symmetric(horizontal: 40.w, vertical: 16.h),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: widget.value != null
                      ? Text(widget.value!, style: Palette.h4)
                      : widget.hintText,
                ),
                widget.hasDropdown
                    ? const Icon(Icons.arrow_drop_down)
                    : Container(),
              ],
            ),
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    _focusNode.dispose();
    scrollController.dispose();
    super.dispose();
  }
}
