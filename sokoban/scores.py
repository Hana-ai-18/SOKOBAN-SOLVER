#scores.py 
import json
import os
from datetime import datetime

SCORES_FILE = "scores"

class Scores:
    def __init__(self, game):
        self.game = game

    def load(self):
        
        try:
            with open(SCORES_FILE, "r") as data:
                scores = json.load(data)
                self.game.index_level = scores.get("level", 1)
            self.game.load_level()
            self.game.start()
        except FileNotFoundError:
            print("No saved data")

    def save(self):
       
        level         = self.game.index_level
        elapsed       = round(self.game.elapsed, 2)       
        steps         = self.game.steps
        method        = self.game.current_method if self.game.current_method else "manual"
        now           = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

       
        solver_time   = getattr(self.game, 'solver_time', 0.0)  
        nodes_exp     = getattr(self.game, 'nodes_exp',   0)   

        
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
                "best_time":     None,
                "best_steps":    None,
                "best_solver_t": None,   # thoi gian solver tot nhat (ngan nhat) cho level nay
                "history":       []
            }

        rec = data["records"][key]

       
        if rec["best_time"] is None or elapsed < rec["best_time"]:
            rec["best_time"] = elapsed

        
        if rec["best_steps"] is None or steps < rec["best_steps"]:
            rec["best_steps"] = steps

        
        if solver_time > 0:
            if rec.get("best_solver_t") is None or solver_time < rec["best_solver_t"]:
                rec["best_solver_t"] = solver_time

       
        rec["history"].append({
            "time":          elapsed,      
            "steps":         steps,        
            "method":        method,       
            "solver_time":   solver_time,  
            "nodes_expanded":nodes_exp,    
            "date":          now,
        })
        rec["history"] = rec["history"][-20:]   

      
        with open(SCORES_FILE, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        print(f"[Score saved] Level {level} | {steps} steps | {elapsed}s play | "
              f"{solver_time:.3f}s solver | {nodes_exp} nodes | {method}")

    def get_best(self, level):
        """Tra ve (best_time, best_steps) cua mot level, hoac (None, None) neu chua co"""
        try:
            with open(SCORES_FILE, "r") as f:
                data = json.load(f)
            rec = data.get("records", {}).get(str(level), {})
            return rec.get("best_time"), rec.get("best_steps")
        except (FileNotFoundError, json.JSONDecodeError):
            return None, None

    def get_best_solver(self, level):
        """
        Tra ve best_solver_t (thoi gian solver ngan nhat) cua mot level.
        Tra ve None neu chua co hoac chua tung dung auto mode.
        """
        try:
            with open(SCORES_FILE, "r") as f:
                data = json.load(f)
            rec = data.get("records", {}).get(str(level), {})
            return rec.get("best_solver_t")
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def get_history(self, level):
        """Tra ve list history cua mot level"""
        try:
            with open(SCORES_FILE, "r") as f:
                data = json.load(f)
            return data.get("records", {}).get(str(level), {}).get("history", [])
        except (FileNotFoundError, json.JSONDecodeError):
            return []