import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/components/main_input_field.dart';
import 'package:structure/config/palette.dart';
import 'package:structure/viewModel/my_page/delete_user_view_model.dart';

class DeleteUserScreen extends StatefulWidget {
  const DeleteUserScreen({
    super.key,
  });

  @override
  State<DeleteUserScreen> createState() => _DeleteUserScreenState();
}

class _DeleteUserScreenState extends State<DeleteUserScreen> {
  @override
  Widget build(BuildContext context) {
    DeleteUserViewModel deleteUserViewModel =
        context.watch<DeleteUserViewModel>();

    return Scaffold(
      appBar: const CustomAppBar(title: '회원 탈퇴'),
      body: Stack(
        children: [
          GestureDetector(
            onTap: () => FocusScope.of(context).unfocus(),
            child: Form(
              key: deleteUserViewModel.formKey,
              child: Container(
                margin: EdgeInsets.symmetric(horizontal: 40.w),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SizedBox(height: 24.h),

                    // 비밀번호 입력
                    Text('비밀번호', style: Palette.h5SemiBoldSecondary),
                    SizedBox(height: 16.h),

                    // 비밀번호 Input Field
                    MainInputField(
                      width: double.infinity,
                      keyboardType: TextInputType.visiblePassword,
                      formKey: deleteUserViewModel.formKey,
                      controller: deleteUserViewModel.password,
                      obscureText: true,
                      validateFunc: (value) =>
                          deleteUserViewModel.pwValidate(value),
                    ),
                    const Spacer(),

                    // 회원 탈퇴 버튼
                    Container(
                      margin: EdgeInsets.only(bottom: 40.h),
                      child: MainButton(
                        width: double.infinity,
                        height: 96.h,
                        text: '회원 탈퇴',
                        onPressed: deleteUserViewModel.isValid()
                            ? () async => deleteUserViewModel.deleteUser()
                            : null,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          deleteUserViewModel.isLoading
              ? const Center(child: LoadingScreen())
              : Container(),
        ],
      ),
    );
  }
}
