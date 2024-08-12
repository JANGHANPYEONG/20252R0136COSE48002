import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/components/main_input_field.dart';
import 'package:structure/config/palette.dart';
import 'package:structure/viewModel/my_page/user_detail_view_model.dart';

class UserDetailScreen extends StatelessWidget {
  const UserDetailScreen({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    UserDetailViewModel userDetailViewModel =
        context.watch<UserDetailViewModel>();

    return GestureDetector(
      onTap: () => FocusScope.of(context).unfocus(),
      child: Scaffold(
        appBar: const CustomAppBar(title: '상세정보 변경'),
        resizeToAvoidBottomInset: false,
        body: Stack(
          children: [
            Container(
              margin: EdgeInsets.symmetric(horizontal: 40.w),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  SizedBox(height: 24.h),

                  // 주소
                  Text('주소', style: Palette.h5SemiBold),
                  SizedBox(height: 16.h),

                  // 주소 입력 textfield
                  Stack(
                    children: [
                      MainInputField(
                        width: double.infinity,
                        controller: userDetailViewModel.mainAddress,
                        readonly: true,
                        hintText: '주소',
                        contentPadding:
                            EdgeInsets.only(left: 24.w, right: 200.w),
                      ),
                      Positioned(
                        right: 24.w,
                        child: TextButton(
                          onPressed: () async => await userDetailViewModel
                              .clickedSearchButton(context),
                          child: Text('검색', style: Palette.h4Regular),
                        ),
                      ),
                    ],
                  ),
                  SizedBox(height: 16.h),

                  // 상세 주소
                  MainInputField(
                    width: double.infinity,
                    readonly: userDetailViewModel.mainAddress.text.isEmpty
                        ? true
                        : false,
                    controller: userDetailViewModel.subAddress,
                    onChangeFunc: (value) =>
                        userDetailViewModel.onChangedSubAdress(value),
                    hintText: '상세주소 (동/호수)',
                  ),
                  SizedBox(height: 32.h),

                  // 회사 정보
                  Text('회사정보', style: Palette.h5SemiBold),
                  SizedBox(height: 16.h),

                  // 회사명
                  MainInputField(
                    width: double.infinity,
                    controller: userDetailViewModel.company,
                    hintText: '회사명',
                    onChangeFunc: (value) =>
                        userDetailViewModel.onChangedCompany(value),
                  ),
                  SizedBox(height: 16.h),

                  // 부서명
                  SizedBox(
                    width: double.infinity,
                    child: Row(
                      children: [
                        // qntjaud
                        Expanded(
                          child: MainInputField(
                            width: double.infinity,
                            controller: userDetailViewModel.department,
                            onChangeFunc: (value) =>
                                userDetailViewModel.onChangedDepartment(value),
                            hintText: '부서명',
                          ),
                        ),
                        SizedBox(width: 16.w),

                        // 직위
                        Expanded(
                          child: MainInputField(
                            width: double.infinity,
                            controller: userDetailViewModel.jobTitle,
                            onChangeFunc: (value) =>
                                userDetailViewModel.onChangedJobTitle(value),
                            hintText: '직위',
                          ),
                        ),
                      ],
                    ),
                  ),

                  // 알림 수신
                  Row(
                    children: [
                      Checkbox(
                        value: userDetailViewModel.isChecked ? true : false,
                        onChanged: (value) =>
                            userDetailViewModel.clicked1stCheckBox(value!),
                        shape: const CircleBorder(),
                        activeColor: Palette.primary,
                        checkColor: Colors.white,
                      ),
                      Text('(선택) 알림 수신 동의', style: Palette.h5),
                    ],
                  ),
                  const Spacer(),

                  Container(
                    margin: EdgeInsets.only(bottom: 40.h),
                    child: MainButton(
                      width: double.infinity,
                      height: 96.h,
                      text: '저장',
                      onPressed: userDetailViewModel.isActivateButton
                          ? () async {
                              await userDetailViewModel
                                  .clickedSaveButton(context);
                            }
                          : null,
                    ),
                  ),
                ],
              ),
            ),
            userDetailViewModel.isLoading
                ? const Center(child: LoadingScreen())
                : Container(),
          ],
        ),
      ),
    );
  }
}
