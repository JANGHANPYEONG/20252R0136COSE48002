//
//
// 육류 분류 페이지(수정 불가!) : Normal
//
//
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/custom_drop_down.dart';
import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/viewModel/data_management/normal/not_editable/insertion_meat_info_not_editable_view_model.dart';

class InsertionMeatInfoNotEditableScreen extends StatefulWidget {
  const InsertionMeatInfoNotEditableScreen({super.key});

  @override
  State<InsertionMeatInfoNotEditableScreen> createState() =>
      _InsertionMeatInfoNotEditableScreenState();
}

class _InsertionMeatInfoNotEditableScreenState
    extends State<InsertionMeatInfoNotEditableScreen> {
  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => FocusScope.of(context).unfocus(),
      child: Scaffold(
        backgroundColor: Colors.white,
        resizeToAvoidBottomInset: false,
        appBar: const CustomAppBar(
          title: '육류 기본정보',
          backButton: true,
          closeButton: false,
        ),
        body: Column(
          children: [
            Container(
              margin: EdgeInsets.symmetric(horizontal: 50.w),
              child: Column(
                children: [
                  SizedBox(
                    height: 70.h,
                  ),
                  Row(
                    children: [
                      Text('종류', style: Palette.h4),
                    ],
                  ),
                  SizedBox(
                    height: 20.h,
                  ),
                  Row(
                    children: [
                      Container(
                        decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(10.sp),
                            color: Palette.fieldEmptyBg),
                        width: 121.w,
                        height: 62.h,
                        child: Center(
                          child: Text(
                            context
                                .read<InsertionMeatInfoNotEditableViewModel>()
                                .speciesValue,
                            style: Palette.h4,
                          ),
                        ),
                      ),
                    ],
                  ),
                  SizedBox(
                    height: 42.0.h,
                  ),
                  Row(
                    children: [
                      Text('부위', style: Palette.h4),
                    ],
                  ),
                  SizedBox(
                    height: 20.h,
                  ),
                  CustomDropdown(
                    hintText: Text(
                        context
                            .read<InsertionMeatInfoNotEditableViewModel>()
                            .primalValue,
                        style: Palette.h4),
                    value: null,
                    itemList: const [],
                    onChanged: null,
                  ),
                  SizedBox(
                    height: 16.h,
                  ),
                  CustomDropdown(
                    hintText: Text(
                        context
                            .read<InsertionMeatInfoNotEditableViewModel>()
                            .secondaryValue,
                        style: Palette.h4),
                    value: null,
                    itemList: const [],
                    onChanged: null,
                  ),
                ],
              ),
            ),
            const Spacer(),
          ],
        ),
      ),
    );
  }
}
