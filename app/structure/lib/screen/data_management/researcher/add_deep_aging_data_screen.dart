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
import 'package:structure/components/data_field.dart';

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
          padding: EdgeInsets.all(35.h),
          child: Column(
            children: [
              Expanded(
                child: SingleChildScrollView(
                  child: Column(
                    children: [
                      Row(
                        children: [
                          Text('딥에이징 일자', style: Palette.h4),
                        ],
                      ),
                      SizedBox(height: 25.h),
                      Consumer<AddDeepAgingDataViewModel>(
                        // 딥에이징 날짜
                        builder: (context, viewModel, child) => InkWell(
                          onTap: () {
                            viewModel.changeState('선택');
                          },
                          child: Container(
                            height: 50.0,
                            decoration: BoxDecoration(
                              color: Palette.fieldEmptyBg,
                              borderRadius: BorderRadius.circular(20.w),
                              // border: Border.all(color: Palette.fieldDisabBg),
                            ),
                            alignment: Alignment.centerLeft,
                            padding: EdgeInsets.only(left: 25.w),
                            child: Text(
                              viewModel.selectedDate,
                              textAlign: TextAlign.center,
                              style: Palette.h5,
                            ),
                          ),
                        ),
                      ),
                      if (context
                          .watch<AddDeepAgingDataViewModel>()
                          .isSelectedDate)
                        CustomTableCalendar(
                            focusedDay: context
                                .watch<AddDeepAgingDataViewModel>()
                                .focused,
                            selectedDay: context
                                .watch<AddDeepAgingDataViewModel>()
                                .selected,
                            onDaySelected: (selectedDay, focusedDay) => context
                                .read<AddDeepAgingDataViewModel>()
                                .onDaySelected(selectedDay, focusedDay)),
                      SizedBox(height: 50.h),
                      Row(
                        children: [
                          Text('초음파 처리 시간', style: Palette.h4),
                        ],
                      ),
                      SizedBox(
                        height: 25.h,
                      ),
                      Row(
                        children: [
                          Expanded(
                            flex: 3,
                            // 딥에이징 처리 시간
                            child: MainTextField(
                              validateFunc: null,
                              onSaveFunc: null,
                              onChangeFunc: (value) => context
                                  .read<AddDeepAgingDataViewModel>()
                                  .changeState(value!),
                              mainText: '',
                              width: 229.w,
                              height: 88.h,
                              canAlert: true,
                              controller: context
                                  .read<AddDeepAgingDataViewModel>()
                                  .textEditingController,
                              formatter: [
                                FilteringTextInputFormatter.allow(
                                    RegExp(r'[0-9]'))
                              ],
                              isNum: 1,
                            ),
                            //     DataField(
                            //   mainText: '',
                            //   subText: '',
                            //   controller: context
                            //       .read<AddDeepAgingDataViewModel>()
                            //       .textEditingController,
                            // ),
                          ),
                          Expanded(
                            flex: 2,
                            child: Padding(
                              padding: const EdgeInsets.only(
                                left: 12.0,
                              ),
                              child: Text('분', style: Palette.h4),
                            ),
                          ),
                          const Expanded(
                            flex: 3,
                            child: SizedBox(
                              width: 20.0,
                            ),
                          )
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(
                height: 20.0,
              ),
              MainButton(
                mode: 1,
                text: '저장',
                width: 658.w,
                height: 104.h,
                onPressed:
                    context.watch<AddDeepAgingDataViewModel>().isInsertedMinute
                        ? () async => context
                            .read<AddDeepAgingDataViewModel>()
                            .saveData(context)
                        : null,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
