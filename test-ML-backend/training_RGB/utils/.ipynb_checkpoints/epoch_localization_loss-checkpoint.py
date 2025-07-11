# train, val 1 epoch를 진행하는 함수
# train 모드에서는 train과 validation 진행
# evaluate 모드에서는 validation만 진행
from tqdm import tqdm
import torch
import numpy as np
from sklearn.metrics import r2_score
import mlflow


# n : batch size
# m : number of pairs
# k X k : resolution of the embedding grid
# D : dimension of each token embedding
# x : a tensor of n embedding grids, shape=[n, D, k, k]
def position_sampling(k, m, n):
    pos_1 = torch.randint(k, size=(n, m, 2))
    pos_2 = torch.randint(k, size=(n, m, 2))
    return pos_1, pos_2
def collect_samples(x, pos, n):
    _, c, h, w = x.size()
    x = x.view(n, c, -1).permute(1, 0, 2).reshape(c, -1)
    pos = ((torch.arange(n).long().to(pos.device) * h * w).view(n, 1)
    + pos[:, :, 0] * h + pos[:, :, 1]).view(-1)
    return (x[:, pos]).view(c, n, -1).permute(1, 0, 2)
def dense_relative_localization_loss(x):
    n, D, k, k = x.size()
    pos_1, pos_2 = position_sampling(k, m, n)
    deltaxy = abs((pos_1 - pos_2).float()) # [n, m, 2]
    deltaxy /= k
    pts_1 = collect_samples(x, pos_1, n).transpose(1, 2) # [n, m, D]
    pts_2 = collect_samples(x, pos_2, n).transpose(1, 2) # [n, m, D]
    predxy = MLP(torch.cat([pts_1, pts_2], dim=2))
    return L1Loss(predxy, deltaxy)



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
        running_loss = 0.0
        labmda_ = 0.1
        all_outputs = []
        all_labels = []
        for images, labels in tqdm(train_loader):
            images, labels = images.to(device), labels.to(device).float()

            optimizer.zero_grad()
            outputs, localization_loss = model(images)
            loss = loss_func(outputs, labels)
            
            loss += lambda_ * localization_loss

            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            all_outputs.append(outputs.cpu().detach().numpy())
            all_labels.append(labels.cpu().detach().numpy())

        all_outputs = np.concatenate(all_outputs, axis=0)
        all_labels = np.concatenate(all_labels, axis=0)

        train_loss = running_loss / len(train_loader)
        train_r2_value = r2_score(all_labels, all_outputs, multioutput='uniform_average')  # 통합 R2 score
        train_accuracies = calculate_accuracy(all_labels, all_outputs)
        average_train_accuracies = np.mean(train_accuracies)

        train_losses.append(train_loss) # epoch마다 train loss 저장
        train_r2.append(train_r2_value) # epoch마다 r2 score 저장

        mlflow.log_metric('train_loss', train_loss, step=epoch+1) # mlflow에 train loss 기록
        mlflow.log_metric('train_R2', train_r2_value, step=epoch+1) # mlflow에 train R2 기록

        print(f"\nEpoch {epoch+1} Summary:")
        if fold:
            print(f"Fold: {fold}/{n_folds}")
        print(f"Train Loss: {running_loss / len(train_loader):.3f}")
        print(f"Train R2: {train_r2_value:.3f}")
        print(f"Train Accuracies: {train_accuracies}")
        print(f"Average Train Accuracy: {average_train_accuracies:.3f}")


        ###### Validation ######
        model.eval()
        val_loss = 0.0
        all_val_outputs = []
        all_val_labels = []
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device).float()
                outputs = model(images)
                loss = loss_func(outputs, labels)

                val_loss += loss.item()
                all_val_outputs.append(outputs.cpu().detach().numpy())
                all_val_labels.append(labels.cpu().detach().numpy())

            scheduler.step(val_loss)

            val_loss /= len(val_loader)
            all_val_outputs = np.concatenate(all_val_outputs, axis=0)
            all_val_labels = np.concatenate(all_val_labels, axis=0)
            val_r2_value = r2_score(all_val_labels, all_val_outputs, multioutput='uniform_average')
            val_accuracies = calculate_accuracy(all_val_labels, all_val_outputs)
            average_val_accuracies = np.mean(val_accuracies)

            mlflow.log_metric('val_loss', val_loss, step=epoch + 1)
            mlflow.log_metric('val_R2', val_r2_value, step=epoch + 1)
            mlflow.log_metric('average_val_acc', average_val_accuracies, step=epoch + 1)

            for i, acc in enumerate(val_accuracies): # 각 라벨마다 정확도 출력 
                label_name = label_names[i]
                mlflow.log_metric(f'val_acc_{label_name}', acc, step=epoch + 1)

            # 가장 낮은 val_loss를 가진 모델 저장
            if val_loss < best_val_loss and save_model:
                best_val_loss = val_loss
                mlflow.pytorch.log_model(model, "best_model")
                print("model saved")

            val_losses.append(val_loss)
            val_r2.append(val_r2_value)
            val_acc.append(val_accuracies)
            average_val_acc.append(average_val_accuracies)

            print(f"\nValidation Results:")
            if fold:
                print(f"Fold: {fold}/{n_folds}")
            print(f"Epoch: {epoch+1}/{num_epochs}")
            print(f"Validation Loss: {val_loss:.3f}")
            print(f"Validation R2: {val_r2_value:.3f}")
            print(f"Validation Accuracies: {val_accuracies}")
            print(f"Average Validation Accuracy: {average_val_accuracies:.3f}")

    return [train_losses, train_r2, val_losses, val_r2, val_acc, average_val_acc]



# 정확도 계산
def calculate_accuracy(labels, outputs):
    accuracies = []
    for i in range(labels.shape[1]):
        correct = ((labels[:, i] - 1) <= outputs[:, i]) & (outputs[:, i] <= (labels[:, i] + 1))
        accuracy = correct.sum() / len(labels)
        accuracies.append(accuracy)
    return accuracies
