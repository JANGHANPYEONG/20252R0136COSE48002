//
//
// 딥에이징 데이터 추가 페이지(View) : Researcher
//
//

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/custom_table_calendar.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/components/main_text_field.dart';
import 'package:structure/config/palette.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/viewModel/data_management/researcher/add_deep_aging_data_view_model.dart';

class AddDeepAgingDataScreen extends StatefulWidget {
  const AddDeepAgingDataScreen({super.key});

  @override
  State<AddDeepAgingDataScreen> createState() => _AddDeepAgingDataScreenState();
}

class _AddDeepAgingDataScreenState extends State<AddDeepAgingDataScreen> {
  @override
  Widget build(BuildContext context) {
    AddDeepAgingDataViewModel addDeepAgingDataViewModel =
        context.watch<AddDeepAgingDataViewModel>();

    return Scaffold(
      appBar: const CustomAppBar(
        title: '딥에이징 데이터',
        backButton: true,
        closeButton: false,
      ),
      resizeToAvoidBottomInset: false,
      body: GestureDetector(
        onTap: () {
          FocusScope.of(context).unfocus();
        },
        child: Stack(
          children: [
            Container(
              margin: EdgeInsets.symmetric(horizontal: 40.w),
              child: Column(
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      SizedBox(height: 24.h),

                      // 딥에이징 일자
                      Text('딥에이징 일자', style: Pallete.h4),
                      SizedBox(height: 16.h),

                      // 딥에이징 일자 container
                      GestureDetector(
                        onTap: () {
                          addDeepAgingDataViewModel.changeState('선택');
                        },
                        child: Container(
                          height: 88.h,
                          decoration: BoxDecoration(
                            color: Palette.onPrimaryContainer,
                            borderRadius: BorderRadius.circular(20.r),
                          ),
                          alignment: Alignment.centerLeft,
                          padding: EdgeInsets.only(left: 24.w),
                          child: Text(
                            addDeepAgingDataViewModel.selectedDate,
                            textAlign: TextAlign.center,
                            style: Palette.h5,
                          ),
                        ),
                      ),

                      // 달력
                      // TODO : 날짜 선택시 닫기
                      if (addDeepAgingDataViewModel.isSelectedDate)
                        CustomTableCalendar(
                          focusedDay: addDeepAgingDataViewModel.focused,
                          selectedDay: addDeepAgingDataViewModel.selected,
                          onDaySelected: (selectedDay, focusedDay) =>
                              addDeepAgingDataViewModel.onDaySelected(
                                  selectedDay, focusedDay),
                        ),
                      SizedBox(height: 32.h),

                      // 초음파 처리 시간
                      Text('초음파 처리 시간', style: Palette.h4),
                      SizedBox(height: 16.h),

                      // 초음파 처리 시간 입력
                      // TODO : 온탭시 닫기
                      Row(
                        children: [
                          Expanded(
                            flex: 3,
                            // 딥에이징 처리 시간
                            child: MainTextField(
                              width: double.infinity,
                              height: 88.h,
                              mainText: '',
                              validateFunc: null,
                              onSaveFunc: null,
                              onChangeFunc: (value) =>
                                  addDeepAgingDataViewModel.changeState(value!),
                              canAlert: true,
                              controller: addDeepAgingDataViewModel
                                  .textEditingController,
                              formatter: [
                                FilteringTextInputFormatter.allow(
                                    RegExp(r'[0-9]'))
                              ],
                              isNum: 1,
                            ),
                          ),
                          SizedBox(width: 16.w),

                          // 분 text
                          Expanded(
                            flex: 2,
                            child: Text('분', style: Pallete.h4),
                          ),
                          const Expanded(
                            flex: 3,
                            child: SizedBox(width: double.infinity),
                          )
                        ],
                      ),
                    ],
                  ),
                  const Spacer(),

                  // 저장 버튼
                  Container(
                    margin: EdgeInsets.only(bottom: 40.h),
                    child: MainButton(
                      width: double.infinity,
                      height: 96.h,
                      text: '저장',
                      onPressed: addDeepAgingDataViewModel.isInsertedMinute
                          ? () async =>
                              addDeepAgingDataViewModel.saveData(context)
                          : null,
                    ),
                  ),
                ],
              ),
            ),
            addDeepAgingDataViewModel.isLoading
                ? const Center(child: LoadingScreen())
                : Container()
          ],
        ),
      ),
    );
  }
}
