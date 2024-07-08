//
//
// CustomDropDown 위젯.
// 데이터 등록 과정 중, 육류 분류를 지정할 때 사용된다.
//
// 파라미터로는
// 1. 현재 분류 값이 표시될 위젯 (대분류 / 소분류 텍스트가 들어감.)
// 2. 선택된 값이 표시될 텍스트 (현재 선택된 분류 값)
// 3. 분류 목록 (각 분류에 맞는 목록이 들어간 리스트)
// 4. DropDown 위젯을 선택할 때, 기능을 수행할 함수
//
//

import 'package:structure/config/pallete.dart';
import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

class CustomDropdown extends StatefulWidget {
  final Widget hintText;
  final String? value;
  final List<String> itemList;
  final Function(String?)? onChanged;

  const CustomDropdown({
    super.key,
    required this.hintText,
    required this.value,
    required this.itemList,
    required this.onChanged,
  });

  @override
  State<CustomDropdown> createState() => _CustomDropdownState();
}

class _CustomDropdownState extends State<CustomDropdown> {
  final LayerLink _layerLink = LayerLink();
  OverlayEntry? _overlayEntry;

  void _toggleDropdown() {
    if (_overlayEntry == null) {
      _overlayEntry = _createOverlayEntry();
      Overlay.of(context).insert(_overlayEntry!);
    } else {
      _overlayEntry!.remove();
      _overlayEntry = null;
    }
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
                borderRadius: BorderRadius.circular(15.sp),
                border: Border.all(
                  color: Palette.meatRegiCardBg,
                ),
              ),
              constraints: BoxConstraints(maxHeight: 400.h),
              child: Scrollbar(
                thumbVisibility: true,
                child: ListView(
                  padding: EdgeInsets.zero,
                  shrinkWrap: true,
                  physics: const ClampingScrollPhysics(),
                  children: widget.itemList.map((String item) {
                    return ListTile(
                      title: Text(item, style: Palette.dropDownTextStyle),
                      onTap: () {
                        widget.onChanged!(item);
                        _toggleDropdown();
                      },
                    );
                  }).toList(),
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
        child: Container(
          decoration: BoxDecoration(
            color: Palette.fieldEmptyBg,
            borderRadius: BorderRadius.circular(15.sp),
            border: Border.all(
              color: widget.value != null
                  ? Palette.meatRegiCardBg
                  : Palette.fieldEmptyBg,
              width: 1.0,
            ),
          ),
          padding: EdgeInsets.symmetric(horizontal: 40.w, vertical: 12),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: widget.value != null
                    ? Text(
                        widget.value!,
                        style: Palette.dropDownTextStyle,
                      )
                    : widget.hintText,
              ),
              const Icon(Icons.arrow_drop_down),
            ],
          ),
        ),
      ),
    );
  }
}
