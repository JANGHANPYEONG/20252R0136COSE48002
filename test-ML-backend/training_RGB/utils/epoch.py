# train, val 1 epoch를 진행하는 함수
# train 모드에서는 train과 validation 진행
# evaluate 모드에서는 validation만 진행
from tqdm import tqdm
import torch
import numpy as np
from sklearn.metrics import r2_score, accuracy_score
import mlflow

from .step import step

def regression(model, params):
    num_epochs = params['num_epochs']
    optimizer = params['optimizer']
    train_loader = params['train_dl']
    val_loader = params['val_dl']
    scheduler = params['scheduler']
    save_model = params['save_model']
    loss_func = params['loss_func']
    fold, n_folds = params['fold']
    label_names = params['label_names']
    train_type = params.get('train_type', None)

    print("save model:", save_model)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    best_val_loss = float('inf')
    train_losses = []
    val_losses = []
    train_r2 = []
    val_r2 = []
    val_acc = []
    average_val_acc = []

    for epoch in range(num_epochs):
        print(f"\n{'-'*15} Epoch {epoch+1}/{num_epochs} {'-'*15}", end='')
        if fold:
            print(f" (Fold {fold}/{n_folds})\n")
        else:
            print()

        ###### Train ######
        model.train()
        #running_loss = 0.0
        running_losses = {}
        all_outputs = []
        all_labels = []
        for images, labels, grade in tqdm(train_loader):
            images, labels = images.to(device), labels.to(device).float()

            # optimizer.zero_grad()
            # outputs = model(images)
            # loss = loss_func(outputs, labels)
            # loss.backward()
            # optimizer.step()

            all_losses, outputs = step(images, labels, train_type, optimizer, model, loss_func, params, grade, train=True)

            # loss = all_loss['loss']
            # running_loss += loss.item()

            # all_loss의 키를 발견했을 때 running_losses 초기화
            if not running_losses:  # running_losses가 비어 있을 경우
                running_losses = {key: 0.0 for key in all_losses.keys()}

            # 각 loss를 running_losses에 더함
            for key, value in all_losses.items():
                running_losses[key] += value.item()
                
            all_outputs.append(outputs.cpu().detach().numpy())
            all_labels.append(labels.cpu().detach().numpy())

        all_outputs = np.concatenate(all_outputs, axis=0)
        all_labels = np.concatenate(all_labels, axis=0)

        average_losses = {key: value / len(train_loader) for key, value in running_losses.items()}

        train_loss = average_losses.get('loss', 0.0)
        #train_loss = running_loss / len(train_loader)
        train_r2_value = r2_score(all_labels, all_outputs, multioutput='uniform_average')  # 통합 R2 score
        train_accuracies = calculate_accuracy(all_labels, all_outputs, [1.0])
        average_train_accuracies = np.mean(train_accuracies)

        train_losses.append(train_loss) # epoch        train_losses.append(train_loss) # epoch마다 train loss 저장
        train_r2.append(train_r2_value) # epoch        train_r2.append(train_r2_value) # epoch마다 r2 score 저장

        # mlflow.log_metric('train_loss', train_loss, step=epoch+1) # mlflow에 train loss 기록
        # mlflow.log_metric('train_R2', train_r2_value, step=epoch+1) # mlflow에 train R2 기록
        # mlflow에 모든 손실 기록
        for key, value in average_losses.items():
            mlflow.log_metric(f'train_{key}', value, step=epoch + 1)

        mlflow.log_metric('train_R2', train_r2_value, step=epoch + 1)

        print(f"\nEpoch {epoch+1} Summary:")
        if fold:
            print(f"Fold: {fold}/{n_folds}")
        for key, value in average_losses.items():
            print(f"Train {key}: {value:.3f}")
        #print(f"Train Loss: {train_loss:.3f}")
        print(f"Train R2: {train_r2_value:.3f}")
        print(f"Train Accuracies (±1.0): {train_accuracies}")
        print(f"Average Train Accuracy (±1.0): {average_train_accuracies:.3f}")


        ###### Validation ######
        model.eval()
        running_val_losses = {}
        #val_loss = 0.0
        all_val_outputs = []
        all_val_labels = []
        with torch.no_grad():
            for images, labels, grade in val_loader:
                images, labels = images.to(device), labels.to(device).float()
                # outputs = model(images)
                # loss = loss_func(outputs, labels)
                all_losses, outputs = step(images, labels, train_type, optimizer, model, loss_func, params, grade)

                # all_losses의 키를 발견했을 때 running_val_losses 초기화
                if not running_val_losses:  # running_val_losses가 비어 있을 경우
                    running_val_losses = {key: 0.0 for key in all_losses.keys()}

                # 각 loss를 running_val_losses에 더함
                for key, value in all_losses.items():
                    running_val_losses[key] += value.item()

                # val_loss += loss.item()
                all_val_outputs.append(outputs.cpu().detach().numpy())
                all_val_labels.append(labels.cpu().detach().numpy())

            # scheduler.step(val_loss)

            average_val_losses = {key: value / len(val_loader) for key, value in running_val_losses.items()}

            val_loss = average_val_losses.get('loss', 0.0)
            # val_loss /= len(val_loader)
            all_val_outputs = np.concatenate(all_val_outputs, axis=0)
            all_val_labels = np.concatenate(all_val_labels, axis=0)
            val_r2_value = r2_score(all_val_labels, all_val_outputs, multioutput='uniform_average')
            val_accuracies_05 = calculate_accuracy(all_val_labels, all_val_outputs, [0.5])
            val_accuracies_10 = calculate_accuracy(all_val_labels, all_val_outputs, [1.0])
            val_accuracies_20 = calculate_accuracy(all_val_labels, all_val_outputs, [2.0])
            average_val_accuracies_05 = np.mean(val_accuracies_05)
            average_val_accuracies_10 = np.mean(val_accuracies_10)
            average_val_accuracies_20 = np.mean(val_accuracies_20)

            scheduler.step(val_loss)

            for key, value in average_val_losses.items():
                mlflow.log_metric(f'val_{key}', value, step=epoch + 1)
            #mlflow.log_metric('val_loss', val_loss, step=epoch + 1)
            mlflow.log_metric('val_R2', val_r2_value, step=epoch + 1)
            mlflow.log_metric('average_val_acc_05', average_val_accuracies_05, step=epoch + 1)
            mlflow.log_metric('average_val_acc_10', average_val_accuracies_10, step=epoch + 1)
            mlflow.log_metric('average_val_acc_20', average_val_accuracies_20, step=epoch + 1)

            for i, (acc_05, acc_10, acc_20) in enumerate(zip(val_accuracies_05, val_accuracies_10, val_accuracies_20)):
                label_name = label_names[i]
                mlflow.log_metric(f'val_acc_05_{label_name}', acc_05, step=epoch + 1)
                mlflow.log_metric(f'val_acc_10_{label_name}', acc_10, step=epoch + 1)
                mlflow.log_metric(f'val_acc_20_{label_name}', acc_20, step=epoch + 1)

            # 가장 낮은 val_loss를 가진 모델 저장
            if val_loss < best_val_loss and save_model:
                best_val_loss = val_loss
                mlflow.pytorch.log_model(model, "best_model")
                print("model saved")

            val_losses.append(val_loss)
            val_r2.append(val_r2_value)
            val_acc.append((val_accuracies_05, val_accuracies_10, val_accuracies_20))
            average_val_acc.append((average_val_accuracies_05, average_val_accuracies_10, average_val_accuracies_20))

            print(f"\nValidation Results:")
            if fold:
                print(f"Fold: {fold}/{n_folds}")
            print(f"Epoch: {epoch+1}/{num_epochs}")
            for key, value in average_val_losses.items():
                print(f"Validation {key}: {value:.3f}")
            #print(f"Validation Loss: {val_loss:.3f}")
            print(f"Validation R2: {val_r2_value:.3f}")
            print(f"Validation Accuracies (±0.5): {val_accuracies_05}")
            print(f"Validation Accuracies (±1.0): {val_accuracies_10}")
            print(f"Validation Accuracies (±2.0): {val_accuracies_20}")
            print(f"Average Validation Accuracy (±0.5): {average_val_accuracies_05:.3f}")
            print(f"Average Validation Accuracy (±1.0): {average_val_accuracies_10:.3f}")
            print(f"Average Validation Accuracy (±2.0): {average_val_accuracies_20:.3f}")

    return [train_losses, train_r2, val_losses, val_r2, val_acc, average_val_acc]

def classification(model, params):
    num_epochs = params['num_epochs']
    optimizer = params['optimizer']
    train_loader = params['train_dl']
    val_loader = params['val_dl']
    scheduler = params['scheduler']
    save_model = params['save_model']
    loss_func = params['loss_func']
    fold, n_folds = params['fold']
    label_names = ['암', '거']

    print("save model:", save_model)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    best_val_loss = float('inf')
    train_losses = []
    val_losses = []
    train_accuracies = []
    val_accuracies = []

    for epoch in range(num_epochs):
        print(f"\n{'-'*15} Epoch {epoch+1}/{num_epochs} {'-'*15}", end='')
        if fold:
            print(f" (Fold {fold}/{n_folds})\n")
        else:
            print()

        ###### Train ######
        model.train()
        running_loss = 0.0
        all_outputs = []
        all_labels = []
        for images, labels in tqdm(train_loader):
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            labels = labels.view(-1)
            labels = labels.long()

            loss = loss_func(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            all_outputs.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

        train_loss = running_loss / len(train_loader)
        train_accuracy = accuracy_score(all_labels, all_outputs)

        train_losses.append(train_loss)
        train_accuracies.append(train_accuracy)

        mlflow.log_metric('train_loss', train_loss, step=epoch+1)
        mlflow.log_metric('train_accuracy', train_accuracy, step=epoch+1)

        print(f"\nEpoch {epoch+1} Summary:")
        if fold:
            print(f"Fold: {fold}/{n_folds}")
        print(f"Train Loss: {train_loss:.3f}")
        print(f"Train Accuracy: {train_accuracy:.3f}")

        ###### Validation ######
        model.eval()
        val_loss = 0.0
        all_val_outputs = []
        all_val_labels = []
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                labels = labels.view(-1)
                labels = labels.long()
                loss = loss_func(outputs, labels)

                val_loss += loss.item()
                _, predicted = torch.max(outputs, 1)
                all_val_outputs.extend(predicted.cpu().numpy())
                all_val_labels.extend(labels.cpu().numpy())

            scheduler.step(val_loss)

            val_loss /= len(val_loader)
            val_accuracy = accuracy_score(all_val_labels, all_val_outputs)

            mlflow.log_metric('val_loss', val_loss, step=epoch + 1)
            mlflow.log_metric('val_accuracy', val_accuracy, step=epoch + 1)

            # 가장 낮은 val_loss를 가진 모델 저장
            if val_loss < best_val_loss and save_model:
                best_val_loss = val_loss
                mlflow.pytorch.log_model(model, "best_model")
                print("model saved")

            val_losses.append(val_loss)
            val_accuracies.append(val_accuracy)

            print(f"\nValidation Results:")
            if fold:
                print(f"Fold: {fold}/{n_folds}")
            print(f"Epoch: {epoch+1}/{num_epochs}")
            print(f"Validation Loss: {val_loss:.3f}")
            print(f"Validation Accuracy: {val_accuracy:.3f}")

    return [train_losses, train_accuracies, val_losses, val_accuracies]

# 정확도 계산
def calculate_accuracy(labels, outputs, tolerances):
    accuracies = []
    for tol in tolerances:
        acc_per_tol = []
        for i in range(labels.shape[1]):
            correct = ((labels[:, i] - tol) <= outputs[:, i]) & (outputs[:, i] <= (labels[:, i] + tol))
            accuracy = correct.sum() / len(labels)
            acc_per_tol.append(accuracy)
        accuracies.append(acc_per_tol)
    return accuracies[0] if len(tolerances) == 1 else accuracies
