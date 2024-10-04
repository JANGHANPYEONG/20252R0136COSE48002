import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/components/main_input_field.dart';
import 'package:structure/config/palette.dart';
import 'package:structure/viewModel/sign_up/insertion_user_detail_view_model.dart';

class InsertionUserDetailScreen extends StatefulWidget {
  const InsertionUserDetailScreen({
    super.key,
  });

  @override
  State<InsertionUserDetailScreen> createState() =>
      _InsertionUserDetailScreenState();
}

class _InsertionUserDetailScreenState extends State<InsertionUserDetailScreen> {
  @override
  Widget build(BuildContext context) {
    InsertionUserDetailViewModel insertionUserDetailViewModel =
        context.watch<InsertionUserDetailViewModel>();

    return GestureDetector(
      onTap: () => FocusScope.of(context).unfocus(),
      child: Scaffold(
        appBar: const CustomAppBar(title: '회원가입'),
        resizeToAvoidBottomInset: false,
        body: Stack(
          children: [
            Container(
              margin: EdgeInsets.symmetric(horizontal: 40.w),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  SizedBox(height: 24.h),

                  // 자택 주소
                  Text('자택주소', style: Palette.h5SemiBoldSecondary),
                  SizedBox(height: 16.h),

                  // 주소
                  Stack(
                    children: [
                      MainInputField(
                        width: double.infinity,
                        controller:
                            insertionUserDetailViewModel.mainAddressController,
                        readonly: true,
                        hintText: '주소',
                        contentPadding:
                            EdgeInsets.only(left: 24.w, right: 200.w),
                      ),
                      Positioned(
                        right: 24.w,
                        child: TextButton(
                          onPressed: () async => insertionUserDetailViewModel
                              .clickedSearchButton(),
                          child: Text('검색', style: Palette.h4Regular),
                        ),
                      ),
                    ],
                  ),
                  SizedBox(height: 16.h),

                  // 상세 주소
                  MainInputField(
                    width: double.infinity,
                    readonly: insertionUserDetailViewModel
                            .mainAddressController.text.isEmpty
                        ? true
                        : false,
                    onChangeFunc: (value) =>
                        insertionUserDetailViewModel.subHomeAdress = value,
                    hintText: '상세주소 (동/호수)',
                  ),
                  SizedBox(height: 16.h),

                  // 회사 정보
                  Text('회사 정보', style: Palette.h5SemiBoldSecondary),
                  SizedBox(height: 16.h),

                  // 회사명
                  MainInputField(
                    width: double.infinity,
                    onChangeFunc: (value) =>
                        insertionUserDetailViewModel.company = value,
                    hintText: '회사명',
                  ),
                  SizedBox(height: 16.h),

                  // 부서명 / 직위
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      // 부서명
                      Expanded(
                        child: MainInputField(
                          width: double.infinity,
                          onChangeFunc: (value) =>
                              insertionUserDetailViewModel.department = value,
                          hintText: '부서명',
                        ),
                      ),
                      SizedBox(width: 16.w),

                      // 직위
                      Expanded(
                        child: MainInputField(
                          width: double.infinity,
                          onChangeFunc: (value) =>
                              insertionUserDetailViewModel.jobTitle = value,
                          hintText: '직위',
                        ),
                      ),
                    ],
                  ),
                  const Spacer(),

                  Container(
                    margin: EdgeInsets.only(bottom: 40.h),
                    alignment: Alignment.bottomCenter,
                    child: MainButton(
                      width: double.infinity,
                      height: 96.h,
                      onPressed: () async =>
                          insertionUserDetailViewModel.clickedNextButton(),
                      text: '회원가입',
                    ),
                  ),
                ],
              ),
            ),
            insertionUserDetailViewModel.isLoading
                ? const Center(child: LoadingScreen())
                : Container()
          ],
        ),
      ),
    );
  }
}
