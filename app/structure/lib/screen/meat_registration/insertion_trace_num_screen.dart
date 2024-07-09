//
//
// 육류 이력번호 페이지(View)
//
//

import 'dart:async';

import 'package:provider/provider.dart';
import 'package:structure/components/inner_box.dart';
import 'package:structure/components/main_text_field.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/main_button.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:structure/viewModel/meat_registration/insertion_trace_num_view_model.dart';

class InsertionTraceNumScreen extends StatefulWidget {
  const InsertionTraceNumScreen({super.key});

  @override
  State<InsertionTraceNumScreen> createState() =>
      _InsertionTraceNumScreenState();
}

class _InsertionTraceNumScreenState extends State<InsertionTraceNumScreen> {
  // 바코드 이벤트 채널
  EventChannel? _eventChannel;

  // 바코드 스트림 구독
  StreamSubscription<dynamic>? _eventSubscription;

  @override
  void initState() {
    super.initState();
    // 바코드 관련 사전 작업.
    _eventChannel = const EventChannel('com.example.structure/barcode');
    _eventSubscription = _eventChannel!.receiveBroadcastStream().listen(
          (dynamic event) =>
              context.read<InsertionTraceNumViewModel>().getBarcodeValue(event),
        );
  }

  @override
  void dispose() {
    // 이벤트 채널을 닫는다.
    _eventSubscription?.cancel();
    super.dispose();
  }

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
            SizedBox(height: 49.h),
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                SizedBox(width: 20.h),
                Form(
                  key: context.read<InsertionTraceNumViewModel>().formKey,

                  // MainTextField 컴포넌트를 이용하여, textfield를 구현.
                  child: MainTextField(
                    controller: context
                        .watch<InsertionTraceNumViewModel>()
                        .textEditingController,
                    action: TextInputAction.search,
                    formatter: [
                      FilteringTextInputFormatter.allow(RegExp(r'[0-9L]'))
                    ],

                    // 유효성 검사
                    validateFunc: (value) {
                      if (value!.isEmpty || value.length < 12) {
                        return "유효하지 않습니다!";
                      } else {
                        return null;
                      }
                    },

                    // 입력된 텍스트 값(value)을 저장할 때 사용.
                    onSaveFunc: (value) {
                      context.read<InsertionTraceNumViewModel>().traceNum =
                          value!;
                    },

                    // 입력된 텍스트 값(value)이 변경될 때 사용.
                    onChangeFunc: (value) {
                      context.read<InsertionTraceNumViewModel>().traceNum =
                          value;
                    },

                    // field에서 완료 버튼을 누를 때 호출.
                    onFieldFunc: (value) {
                      context.read<InsertionTraceNumViewModel>().traceNum =
                          value;
                      context.read<InsertionTraceNumViewModel>().start(context);
                    },
                    mainText: '이력번호 입력',
                    prefixIcon: GestureDetector(
                      onTap: () {
                        String currentText = context
                            .read<InsertionTraceNumViewModel>()
                            .textEditingController
                            .text;
                        if (currentText.isNotEmpty &&
                            currentText.length >= 12) {
                          context.read<InsertionTraceNumViewModel>().traceNum =
                              currentText;
                          context
                              .read<InsertionTraceNumViewModel>()
                              .start(context);
                        }
                      },
                      child: const Icon(Icons.search, size: 30.0),
                    ),
                    canAlert: true,
                    width: 600.w,
                    height: 115.h,
                    maxLength: 15,
                  ),
                ),

                // 취소 버튼
                SizedBox(
                  width: 50,
                  child: TextButton(
                    onPressed: () {
                      context
                          .read<InsertionTraceNumViewModel>()
                          .clearText(context);
                      FocusScope.of(context).unfocus();
                    },
                    child: const Text(
                      '취소',
                      style: TextStyle(
                        color: Colors.black,
                        fontSize: 14,
                      ),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 5.0),

            // ListTable 위젯을 표현. (모든 데이터가 입력된 상황)
            if (context.watch<InsertionTraceNumViewModel>().isAllInserted == 1)
              Expanded(
                  child: Container(
                width: 642.w,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(50),
                ),
                child: ListTable(
                    tableData:
                        context.read<InsertionTraceNumViewModel>().tableData),
              ))
            // 검색 결과가 존재하지 않음을 출력. (이력 번호가 잘못된 상황)
            else if (context.read<InsertionTraceNumViewModel>().isAllInserted ==
                2)
              const Expanded(
                child: Center(
                  child: Padding(
                    padding: EdgeInsets.only(
                      bottom: 45.0,
                    ),
                    child: Text(
                      '검색결과가 없습니다',
                      style: TextStyle(
                        fontSize: 17.0,
                      ),
                    ),
                  ),
                ),
              )
            // 빈 화면을 표현. (이력 번호 입력이 되지 않은 초기 상태)
            else if (context.read<InsertionTraceNumViewModel>().isAllInserted ==
                0)
              const Spacer(
                flex: 2,
              ),
            Container(
              margin: EdgeInsets.only(bottom: 28.h),
              child: MainButton(
                mode: 1,
                text: '다음',
                width: 658.w,
                height: 104.h,
                // 모든 데이터가 입력된 상황에서 '다음' 버튼을 활성화.
                onPressed:
                    (context.read<InsertionTraceNumViewModel>().isAllInserted ==
                            1)
                        ? () => context
                            .read<InsertionTraceNumViewModel>()
                            .clickedNextbutton(context)
                        : null,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class ListTable extends StatelessWidget {
  ListTable({super.key, required this.tableData});

  // api에서 받아온 데이터가 들어가는 list.
  final List<String?> tableData;
  // table을 설명하는 list이다.
  final List<String> baseData = [
    '이력번호',
    '경영자',
    '사육지',
    '도축일자',
    '육종/축종',
    '성별',
    '등급',
    '출생년월일',
  ];

  @override
  Widget build(BuildContext context) {
    // listview 위젯을 이용하여 위젯 list를 구현.
    return ListView.builder(
      itemCount: baseData.length,
      itemBuilder: (context, index) {
        return IntrinsicHeight(
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // baseData를 이용하여 table index list를 출력.
              Flexible(
                flex: 1,
                fit: FlexFit.tight,
                child: InnerBox(
                  text: baseData[index],
                  style: Palette.listIndexGrey,
                ),
              ),
              // tableData를 이용하여 table data list를 출력.
              Flexible(
                flex: 2,
                fit: FlexFit.tight,
                child: (baseData[index] == '사육지' && (tableData[2] != '돼지'))
                    // 데이터가 '소'이며, '사육지'일 때, 주소가 길어질 수 있으니 스크롤 형태로 출력.
                    ? InnerBox(
                        text: tableData[index],
                        style: Palette.listStyle,
                      )
                    : InnerBox(
                        text:
                            (tableData[index] != null) ? tableData[index] : "",
                        style: Palette.listStyle,
                      ),
              ),
            ],
          ),
        );
      },
    );
  }
}
