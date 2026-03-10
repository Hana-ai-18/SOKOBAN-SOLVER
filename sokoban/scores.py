import json
import os
from datetime import datetime

SCORES_FILE = "scores"

class Scores:
    def __init__(self, game):
        self.game = game

    def load(self):
        """Load level đã lưu gần nhất và bắt đầu từ đó (giữ nguyên hành vi gốc)"""
        try:
            with open(SCORES_FILE, "r") as data:
                scores = json.load(data)
                self.game.index_level = scores.get("level", 1)
            self.game.load_level()
            self.game.start()
        except FileNotFoundError:
            print("No saved data")

    def save(self):
        """
        Lưu scores sau mỗi lần thắng:
        - level cao nhất đã qua (hành vi gốc)
        - bảng records: mỗi level lưu best_time, best_steps, history các lần chơi
        """
        level    = self.game.index_level
        elapsed  = round(self.game.elapsed, 2)
        steps    = self.game.steps
        method   = self.game.current_method if self.game.current_method else "manual"
        now      = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

       
        try:
            with open(SCORES_FILE, "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        
        saved_level = data.get("level", 0)
        if level > saved_level:
            data["level"] = level

        
        if "records" not in data:
            data["records"] = {}

        key = str(level)   

        if key not in data["records"]:
            data["records"][key] = {
                "best_time":  None,
                "best_steps": None,
                "history":    []
            }

        rec = data["records"][key]

       
        if rec["best_time"] is None or elapsed < rec["best_time"]:
            rec["best_time"] = elapsed

       
        if rec["best_steps"] is None or steps < rec["best_steps"]:
            rec["best_steps"] = steps

        
        rec["history"].append({
            "time":   elapsed,
            "steps":  steps,
            "method": method,
            "date":   now,
        })
        rec["history"] = rec["history"][-20:]

       
        with open(SCORES_FILE, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        print(f"[Score saved] Level {level} | {steps} steps | {elapsed}s | {method}")

    def get_best(self, level):
        """Trả về (best_time, best_steps) của một level, hoặc (None, None) nếu chưa có"""
        try:
            with open(SCORES_FILE, "r") as f:
                data = json.load(f)
            rec = data.get("records", {}).get(str(level), {})
            return rec.get("best_time"), rec.get("best_steps")
        except (FileNotFoundError, json.JSONDecodeError):
            return None, None

    def get_history(self, level):
        """Trả về list history của một level"""
        try:
            with open(SCORES_FILE, "r") as f:
                data = json.load(f)
            return data.get("records", {}).get(str(level), {}).get("history", [])
        except (FileNotFoundError, json.JSONDecodeError):
            return []