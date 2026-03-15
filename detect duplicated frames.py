import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog

def get_video_path():
    """탐색기 팝업을 띄워 mp4 파일을 선택합니다."""
    root = tk.Tk()
    root.withdraw() # 메인 윈도우 숨기기
    file_path = filedialog.askopenfilename(
        title="검사할 MP4 영상을 선택하세요",
        filetypes=[("MP4 files", "*.mp4")]
    )
    return file_path

def analyze_video(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("영상을 열 수 없습니다.")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    
    raw_duplicate_frames = [] # 필터링 전의 모든 중복 프레임을 담을 리스트
    
    ret, prev_frame = cap.read()
    if not ret:
        return

    # 화면을 좌우로 나눴을 때 게임 화면이 차지하는 비율 (예: 왼쪽 65%)
    height, width, _ = prev_frame.shape
    game_screen_width = int(width * 0.65) 
    
    # 직전 프레임의 흑백 처리 (연산 속도 향상을 위해)
    prev_game_crop = prev_frame[:, :game_screen_width]
    prev_gray = cv2.cvtColor(prev_game_crop, cv2.COLOR_BGR2GRAY)

    frame_idx = 1
    print(f"분석 시작... (총 FPS: {fps:.2f})")

    while True:
        ret, curr_frame = cap.read()
        if not ret:
            break
            
        # 1. 게임 화면 영역 크롭 및 흑백 변환
        curr_game_crop = curr_frame[:, :game_screen_width]
        curr_gray = cv2.cvtColor(curr_game_crop, cv2.COLOR_BGR2GRAY)

        # 2. 중복 프레임 검사 (Frame Duplication)
        diff = cv2.absdiff(curr_gray, prev_gray)
        non_zero_count = np.count_nonzero(diff > 5) 
        
        # 픽셀 변화가 거의 없다면 멈춘 프레임으로 간주
        if non_zero_count < 1000: 
            raw_duplicate_frames.append(frame_idx)
            
        # 3. 찌그러진 노트 검사 (Problem 1)
        # TODO: 여기에 파란색 색상 마스킹 및 비율(Aspect Ratio) 검사 로직 추가 필요

        # 다음 루프를 위해 현재 프레임을 직전 프레임으로 갱신
        prev_gray = curr_gray
        frame_idx += 1
        
        if frame_idx % 1000 == 0:
            print(f"... {frame_idx} 프레임 분석 중 ...")

    cap.release()
    
    # ==========================================
    # 🎯 [추가된 핵심 로직] 연속 프레임 필터링
    # ==========================================
    # 1. 연속된 프레임 번호들을 그룹으로 묶습니다. (예: [6], [276, 278], [4261, 4262, 4263...])
    groups = []
    current_group = []
    for f in raw_duplicate_frames:
        if not current_group:
            current_group.append(f)
        elif f == current_group[-1] + 1:
            current_group.append(f)
        else:
            groups.append(current_group)
            current_group = [f]
    if current_group:
        groups.append(current_group)
        
    # 2. 길이가 3 이상인 그룹(4프레임 이상 화면이 멈춘 경우)은 기믹/블랙스크린으로 간주하고 제외합니다.
    filtered_duplicates = []
    for g in groups:
        if len(g) < 3: # 1~2개 연속된 경우(2~3프레임 멈춤)만 진짜 에러로 취급
            filtered_duplicates.extend(g)
            
    # ==========================================

    # 결과 출력
    print("\n" + "="*40)
    print("🎬 분석 결과 리포트")
    print("="*40)
    
    print(f"🚨 게임 화면 순간 멈춤 의심 구간: 총 {len(filtered_duplicates)} 프레임 (기믹/블랙스크린 제외)")
    
    # 1. 터미널 출력
    for f in filtered_duplicates: 
        time_sec = f / fps
        print(f"   - 프레임: {f} ({time_sec:.2f}초)")

    # 2. 메모장(.txt) 파일 저장
    report_path = video_path.replace(".mp4", "_에러리포트.txt")
    with open(report_path, "w", encoding="utf-8") as f_out:
        f_out.write(f"🎬 분석 영상: {video_path}\n")
        f_out.write("="*40 + "\n")
        f_out.write(f"🚨 게임 화면 순간 멈춤 의심 구간: 총 {len(filtered_duplicates)} 프레임 (기믹/블랙스크린 제외)\n")
        f_out.write("="*40 + "\n")
        for f in filtered_duplicates:
            time_sec = f / fps
            f_out.write(f"프레임: {f} ({time_sec:.2f}초)\n")
            
    print(f"\n✅ 전체 분석 결과가 메모장 파일로 저장되었습니다:\n 📁 {report_path}")

if __name__ == "__main__":
    video_file = get_video_path()
    if video_file:
        print(f"선택된 파일: {video_file}")
        analyze_video(video_file)
    else:
        print("파일 선택이 취소되었습니다.")