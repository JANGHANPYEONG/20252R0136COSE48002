import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/components/main_input_field.dart';
import 'package:structure/config/palette.dart';
import 'package:structure/viewModel/my_page/change_password_view_model.dart';

class ChangePasswordScreen extends StatefulWidget {
  const ChangePasswordScreen({
    super.key,
  });

  @override
  State<ChangePasswordScreen> createState() => _ChangePasswordScreenState();
}

class _ChangePasswordScreenState extends State<ChangePasswordScreen> {
  @override
  Widget build(BuildContext context) {
    ChangePasswordViewModel changePasswordViewModel =
        context.watch<ChangePasswordViewModel>();

    return Scaffold(
      appBar: const CustomAppBar(
        title: '비밀번호 변경',
        backButton: true,
        closeButton: false,
      ),
      resizeToAvoidBottomInset: false,
      body: Stack(
        children: [
          GestureDetector(
            onTap: () => FocusScope.of(context).unfocus(),
            child: Form(
              key: changePasswordViewModel.formKey,
              child: Container(
                margin: EdgeInsets.symmetric(horizontal: 40.w),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SizedBox(height: 24.h),

                    // 현재 비밀번호
                    Text('현재 비밀번호', style: Palette.h5SemiBoldSecondary),
                    SizedBox(height: 16.h),

                    // 현재 비밀번호 Input Field
                    MainInputField(
                      width: double.infinity,
                      formKey: changePasswordViewModel.formKey,
                      controller: changePasswordViewModel.originPW,
                      obscureText: true,
                      validateFunc: (value) =>
                          changePasswordViewModel.pwValidate(value),
                    ),
                    SizedBox(height: 32.h),

                    // 새 비밀번호
                    Text('새 비밀번호', style: Palette.h5SemiBoldSecondary),
                    SizedBox(height: 16.h),

                    // 새 비밀번호 Input Field
                    MainInputField(
                      width: double.infinity,
                      formKey: changePasswordViewModel.formKey,
                      controller: changePasswordViewModel.newPW,
                      obscureText: true,
                      validateFunc: (value) =>
                          changePasswordViewModel.newPwValidate(value),
                      hintText: '영문 대/소문자+숫자+특수문자',
                    ),
                    SizedBox(height: 16.h),

                    // 비밀번호 확인 Input Field
                    MainInputField(
                      width: double.infinity,
                      formKey: changePasswordViewModel.formKey,
                      controller: changePasswordViewModel.newCPW,
                      obscureText: true,
                      validateFunc: (value) =>
                          changePasswordViewModel.cPwValidate(value),
                      hintText: '비밀번호 확인',
                    ),
                    const Spacer(),

                    // 저장 버튼
                    Container(
                      margin: EdgeInsets.only(bottom: 40.h),
                      child: MainButton(
                        width: double.infinity,
                        height: 96.h,
                        text: '변경',
                        onPressed: changePasswordViewModel.isAllValid() &&
                                changePasswordViewModel.isActivateButton
                            ? () async =>
                                changePasswordViewModel.changePassword(context)
                            : null,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          changePasswordViewModel.isLoading
              ? const Center(child: LoadingScreen())
              : Container(),
        ],
      ),
    );
  }
}
