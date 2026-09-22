import { bootstrapApplication } from "@angular/platform-browser";
import { Component, OnDestroy } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { HttpClient, provideHttpClient } from "@angular/common/http";

@Component({
  selector: "app-root",
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: ` <main>
    <header>
      <h1>TonyAI</h1>
      <span>v0.2.1 • OpenRouter + Ollama Qwen3 8B + .NET 10 + Python</span>
    </header>

    <section class="panel">
      <label>Task</label>
      <textarea
        [(ngModel)]="task"
        placeholder="Create a .NET 10 Employee CRUD API using EF Core and SQL Server"
      ></textarea>

      <div class="row">
        <label>
          Complexity
          <input type="number" min="1" max="10" [(ngModel)]="complexity" />
        </label>

        <label>
          Project
          <input [(ngModel)]="project" />
        </label>

        <button (click)="run()" [disabled]="loading">
          {{ loading ? "Running..." : "Run TonyAI" }}
        </button>
      </div>
    </section>

    <section class="panel">
      <h2>Agent Activity</h2>

      <div *ngIf="loading && taskStatus" class="activity">
        <div class="progress-header">
          <strong>{{ taskStatus.current_step }}</strong>
          <span>{{ taskStatus.progress_percent }}%</span>
        </div>

        <div class="progress-track">
          <div
            class="progress-bar"
            [style.width.%]="taskStatus.progress_percent"
          ></div>
        </div>

        <p class="status-message">{{ taskStatus.message }}</p>

        <div class="stats">
          <div><small>Status</small><strong>{{ taskStatus.status }}</strong></div>
          <div><small>Agent</small><strong>{{ taskStatus.agent || "Selecting..." }}</strong></div>
          <div><small>Provider</small><strong>{{ taskStatus.provider || "Selecting..." }}</strong></div>
          <div><small>Model</small><strong>{{ taskStatus.model || "Selecting..." }}</strong></div>
          <div><small>Started</small><strong>{{ formatTime(taskStatus.start_time) }}</strong></div>
          <div><small>Duration</small><strong>{{ formatDuration(taskStatus.duration_seconds) }}</strong></div>
        </div>
      </div>

      <div *ngIf="result && !result.error">
        <div class="stats">
          <div><small>Agent</small><strong>{{ result.agent }}</strong></div>
          <div><small>Provider</small><strong>{{ result.provider }}</strong></div>
          <div><small>Model</small><strong>{{ result.model }}</strong></div>
          <div><small>Started</small><strong>{{ formatTime(result.start_time) }}</strong></div>
          <div><small>Ended</small><strong>{{ formatTime(result.end_time) }}</strong></div>
          <div><small>Duration</small><strong>{{ formatDuration(result.duration_seconds) }}</strong></div>
        </div>

        <h3>Final Status: {{ result.status }}</h3>
        <h3>Output</h3>
        <pre>{{ result.result }}</pre>
      </div>

      <div *ngIf="result?.error">
        <h3>❌ Error</h3>
        <pre>{{ result.error }}</pre>
      </div>

      <p *ngIf="!result && !loading">No task executed yet.</p>
    </section>

    <section class="panel">
      <h2>System</h2>
      <button (click)="health()">Check AI Providers</button>
      <pre>{{ healthResult | json }}</pre>
    </section>
  </main>`,
  styles: [
    `
      main { max-width: 1100px; margin: 30px auto; padding: 0 20px; font-family: Arial; }
      body { margin: 0; background: #0e0e0e; color: #eee; }
      .panel { background: #171717; border: 1px solid #333; border-radius: 12px; padding: 20px; margin: 16px 0; }
      textarea { width: 100%; min-height: 140px; box-sizing: border-box; background: #0d0d0d; color: #eee; border: 1px solid #444; border-radius: 8px; padding: 12px; }
      .row { display: flex; gap: 20px; align-items: center; flex-wrap: wrap; margin-top: 15px; }
      input { background: #0d0d0d; color: #eee; border: 1px solid #444; padding: 8px; }
      button { padding: 10px 16px; border: 0; border-radius: 7px; cursor: pointer; }
      pre { white-space: pre-wrap; background: #0d0d0d; padding: 14px; border-radius: 8px; }
      .activity { margin-top: 12px; }
      .progress-header { display: flex; justify-content: space-between; margin-bottom: 8px; }
      .progress-track { height: 12px; background: #303030; border-radius: 8px; overflow: hidden; }
      .progress-bar { height: 100%; transition: width 0.4s ease; background: #4caf50; }
      .status-message { color: #bbb; }
      .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin: 16px 0; }
      .stats div { background: #101010; border: 1px solid #2d2d2d; border-radius: 8px; padding: 10px; }
      .stats small { display: block; color: #888; margin-bottom: 5px; }
      .stats strong { word-break: break-word; }
    `,
  ],
})
export class AppComponent implements OnDestroy {
  task = "";
  project = "default";
  complexity = 5;
  loading = false;
  result: any = null;
  taskStatus: any = null;
  healthResult: any = null;
  private pollHandle: ReturnType<typeof setInterval> | null = null;

  constructor(private http: HttpClient) {}

  run() {
    this.stopPolling();
    this.loading = true;
    this.result = null;
    this.taskStatus = null;

    this.http
      .post<any>("http://localhost:5000/api/task", {
        task: this.task,
        project: this.project,
        complexity: this.complexity,
      })
      .subscribe({
        next: (value) => {
          this.pollStatus(value.task_id);
        },
        error: (err) => {
          this.result = {
            error:
              err.error?.detail ||
              err.error?.message ||
              err.message ||
              "Unknown error",
          };
          this.loading = false;
        },
      });
  }

  pollStatus(taskId: string) {
    const check = () => {
      this.http
        .get<any>(`http://localhost:5000/api/task/${taskId}`)
        .subscribe({
          next: (value) => {
            this.taskStatus = value;

            if (value.status === "completed" || value.status === "failed") {
              this.result = value;
              this.loading = false;
              this.stopPolling();
            }
          },
          error: (err) => {
            this.result = {
              error:
                err.error?.detail ||
                err.error?.message ||
                err.message ||
                "Unable to read task status",
            };
            this.loading = false;
            this.stopPolling();
          },
        });
    };

    check();
    this.pollHandle = setInterval(check, 1000);
  }

  stopPolling() {
    if (this.pollHandle) {
      clearInterval(this.pollHandle);
      this.pollHandle = null;
    }
  }

  formatTime(value: string | null) {
    return value ? new Date(value).toLocaleString() : "-";
  }

  formatDuration(seconds: number | null) {
    if (seconds === null || seconds === undefined) return "0s";
    const s = Math.round(seconds);
    const minutes = Math.floor(s / 60);
    const remaining = s % 60;
    return minutes ? `${minutes}m ${remaining}s` : `${remaining}s`;
  }

  health() {
    this.http.get<any>("http://localhost:5000/api/health").subscribe({
      next: (value) => (this.healthResult = value),
      error: (err) => {
        this.healthResult = {
          error:
            err.error?.detail ||
            err.error?.message ||
            err.message ||
            "Unable to reach the gateway",
        };
      },
    });
  }

  ngOnDestroy() {
    this.stopPolling();
  }
}

bootstrapApplication(AppComponent, {
  providers: [provideHttpClient()],
}).catch(console.error);
