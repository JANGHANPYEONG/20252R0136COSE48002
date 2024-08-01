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
      backgroundColor: Colors.white,
      appBar: const CustomAppBar(
        title: '딥에이징 데이터',
        backButton: true,
        closeButton: false,
      ),
      body: GestureDetector(
        onTap: () {
          FocusScope.of(context).unfocus();
        },
        child: Padding(
          padding: EdgeInsets.all(40.w),
          child: Stack(
            children: [
              Column(
                children: [
                  Expanded(
                    child: SingleChildScrollView(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // 딥에이징 일자
                          Text('딥에이징 일자', style: Pallete.h4),
                          SizedBox(height: 25.h),

                          // 딥에이징 일자 container
                          GestureDetector(
                            onTap: () {
                              addDeepAgingDataViewModel.changeState('선택');
                            },
                            child: Container(
                              height: 88.h,
                              decoration: BoxDecoration(
                                color: Pallete.fieldEmptyBg,
                                borderRadius: BorderRadius.circular(20.w),
                              ),
                              alignment: Alignment.centerLeft,
                              padding: EdgeInsets.only(left: 25.w),
                              child: Text(
                                addDeepAgingDataViewModel.selectedDate,
                                textAlign: TextAlign.center,
                                style: Pallete.h5,
                              ),
                            ),
                          ),

                          // 달력
                          if (addDeepAgingDataViewModel.isSelectedDate)
                            CustomTableCalendar(
                              focusedDay: addDeepAgingDataViewModel.focused,
                              selectedDay: addDeepAgingDataViewModel.selected,
                              onDaySelected: (selectedDay, focusedDay) =>
                                  addDeepAgingDataViewModel.onDaySelected(
                                      selectedDay, focusedDay),
                            ),
                          SizedBox(height: 50.h),

                          // 초음파 처리 시간
                          Text('초음파 처리 시간', style: Pallete.h4),
                          SizedBox(height: 25.h),

                          // 초음파 처리 시간 입력
                          Row(
                            children: [
                              Expanded(
                                flex: 3,
                                // 딥에이징 처리 시간
                                child: MainTextField(
                                  validateFunc: null,
                                  onSaveFunc: null,
                                  onChangeFunc: (value) =>
                                      addDeepAgingDataViewModel
                                          .changeState(value!),
                                  mainText: '',
                                  width: 229.w,
                                  height: 88.h,
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

                              // 분 text
                              Expanded(
                                flex: 2,
                                child: Padding(
                                  padding: const EdgeInsets.only(left: 12.0),
                                  child: Text('분', style: Pallete.h4),
                                ),
                              ),
                              const Expanded(
                                  flex: 3, child: SizedBox(width: 20.0))
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 20.0),

                  // 저장 버튼
                  MainButton(
                    mode: 1,
                    text: '저장',
                    width: 658.w,
                    height: 96.h,
                    onPressed: addDeepAgingDataViewModel.isInsertedMinute
                        ? () async =>
                            addDeepAgingDataViewModel.saveData(context)
                        : null,
                  ),
                ],
              ),
              addDeepAgingDataViewModel.isLoading
                  ? const Center(child: LoadingScreen())
                  : Container()
            ],
          ),
        ),
      ),
    );
  }
}
