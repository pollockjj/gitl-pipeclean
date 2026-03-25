#include <algorithm>
#include <array>
#include <iostream>
#include <sstream>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

#include <ext/pb_ds/assoc_container.hpp>
#include <ext/pb_ds/tree_policy.hpp>

using namespace std;
using namespace __gnu_pbds;

namespace {
constexpr int kMaxProblems = 26;
constexpr int kStatusKinds = 4;
}

struct ProblemState {
    int final_wrong = 0;
    bool final_solved = false;
    int final_ac_time = 0;

    int visible_wrong = 0;
    bool visible_solved = false;
    int visible_ac_time = 0;

    bool frozen = false;
    int frozen_post_count = 0;
};

struct Team {
    string name;
    vector<ProblemState> problems;

    int visible_solved = 0;
    int visible_penalty = 0;
    vector<int> visible_solve_times_desc;
    int frozen_problem_count = 0;

    array<array<int, kStatusKinds>, kMaxProblems> latest_submission{};

    void recompute_visible(int problem_count) {
        visible_solved = 0;
        visible_penalty = 0;
        visible_solve_times_desc.clear();
        for (int i = 0; i < problem_count; ++i) {
            const ProblemState& problem = problems[i];
            if (!problem.visible_solved) {
                continue;
            }
            ++visible_solved;
            visible_penalty += problem.visible_wrong * 20 + problem.visible_ac_time;
            visible_solve_times_desc.push_back(problem.visible_ac_time);
        }
        sort(visible_solve_times_desc.begin(), visible_solve_times_desc.end(), greater<int>());
    }
};

struct Contest;
static Contest* g_contest = nullptr;

struct RankCompare {
    bool operator()(int lhs, int rhs) const;
};

using RankTree = tree<int, null_type, RankCompare, rb_tree_tag, tree_order_statistics_node_update>;

struct Contest {
    bool started = false;
    bool frozen = false;
    bool has_flushed = false;
    int problem_count = 0;

    vector<Team> teams;
    unordered_map<string, int> team_id;
    unordered_map<string, int> name_rank_before_first_flush;

    vector<int> ranking_order;
    vector<int> ranking_of_team;

    Contest() {
        g_contest = this;
    }

    static int status_index(const string& status) {
        if (status == "Accepted") {
            return 0;
        }
        if (status == "Wrong_Answer") {
            return 1;
        }
        if (status == "Runtime_Error") {
            return 2;
        }
        return 3;
    }

    bool better_team(int lhs, int rhs) const {
        const Team& a = teams[lhs];
        const Team& b = teams[rhs];
        if (a.visible_solved != b.visible_solved) {
            return a.visible_solved > b.visible_solved;
        }
        if (a.visible_penalty != b.visible_penalty) {
            return a.visible_penalty < b.visible_penalty;
        }
        if (a.visible_solve_times_desc != b.visible_solve_times_desc) {
            return a.visible_solve_times_desc > b.visible_solve_times_desc;
        }
        if (a.name != b.name) {
            return a.name < b.name;
        }
        return lhs < rhs;
    }

    void rebuild_name_ranks() {
        vector<pair<string, int>> names;
        names.reserve(teams.size());
        for (int i = 0; i < static_cast<int>(teams.size()); ++i) {
            names.push_back({teams[i].name, i});
        }
        sort(names.begin(), names.end());
        name_rank_before_first_flush.clear();
        for (int i = 0; i < static_cast<int>(names.size()); ++i) {
            name_rank_before_first_flush[names[i].first] = i + 1;
        }
    }

    void rebuild_ranking_cache_from_sorted_ids(const vector<int>& ids) {
        ranking_order = ids;
        ranking_of_team.assign(teams.size(), 0);
        for (int i = 0; i < static_cast<int>(ranking_order.size()); ++i) {
            ranking_of_team[ranking_order[i]] = i + 1;
        }
    }

    void flush_scoreboard() {
        vector<int> ids(teams.size());
        for (int i = 0; i < static_cast<int>(teams.size()); ++i) {
            ids[i] = i;
        }
        sort(ids.begin(), ids.end(), [this](int lhs, int rhs) {
            return better_team(lhs, rhs);
        });
        rebuild_ranking_cache_from_sorted_ids(ids);
        has_flushed = true;
    }

    string problem_display(const ProblemState& problem) const {
        if (problem.frozen) {
            if (problem.visible_wrong == 0) {
                return "0/" + to_string(problem.frozen_post_count);
            }
            return "-" + to_string(problem.visible_wrong) + "/" + to_string(problem.frozen_post_count);
        }
        if (problem.visible_solved) {
            if (problem.visible_wrong == 0) {
                return "+";
            }
            return "+" + to_string(problem.visible_wrong);
        }
        if (problem.visible_wrong == 0) {
            return ".";
        }
        return "-" + to_string(problem.visible_wrong);
    }

    void print_scoreboard() const {
        for (int team_idx : ranking_order) {
            const Team& team = teams[team_idx];
            cout << team.name << ' ' << ranking_of_team[team_idx] << ' '
                 << team.visible_solved << ' ' << team.visible_penalty;
            for (int i = 0; i < problem_count; ++i) {
                cout << ' ' << problem_display(team.problems[i]);
            }
            cout << '\n';
        }
    }

    void update_final_problem(ProblemState& problem, const string& status, int time) {
        if (problem.final_solved) {
            return;
        }
        if (status == "Accepted") {
            problem.final_solved = true;
            problem.final_ac_time = time;
            return;
        }
        ++problem.final_wrong;
    }

    void update_visible_problem(ProblemState& problem, const string& status, int time) {
        if (problem.visible_solved) {
            return;
        }
        if (status == "Accepted") {
            problem.visible_solved = true;
            problem.visible_ac_time = time;
            return;
        }
        ++problem.visible_wrong;
    }

    void add_team(const string& name) {
        if (started) {
            cout << "[Error]Add failed: competition has started.\n";
            return;
        }
        if (team_id.find(name) != team_id.end()) {
            cout << "[Error]Add failed: duplicated team name.\n";
            return;
        }
        int id = static_cast<int>(teams.size());
        Team team;
        team.name = name;
        team.problems.resize(kMaxProblems);
        teams.push_back(team);
        team_id[name] = id;
        cout << "[Info]Add successfully.\n";
    }

    void start_contest(int problems) {
        if (started) {
            cout << "[Error]Start failed: competition has started.\n";
            return;
        }
        started = true;
        problem_count = problems;
        ranking_of_team.assign(teams.size(), 0);
        rebuild_name_ranks();
        cout << "[Info]Competition starts.\n";
    }

    void submit(char problem_name, const string& team_name, const string& status, int time) {
        int id = team_id[team_name];
        Team& team = teams[id];
        int problem_idx = problem_name - 'A';
        ProblemState& problem = team.problems[problem_idx];

        team.latest_submission[problem_idx][status_index(status)] = time;
        update_final_problem(problem, status, time);

        if (frozen && !problem.visible_solved) {
            if (!problem.frozen) {
                problem.frozen = true;
                ++team.frozen_problem_count;
            }
            ++problem.frozen_post_count;
            return;
        }

        int old_wrong = problem.visible_wrong;
        bool old_solved = problem.visible_solved;
        int old_time = problem.visible_ac_time;
        update_visible_problem(problem, status, time);
        if (problem.visible_wrong != old_wrong || problem.visible_solved != old_solved ||
            problem.visible_ac_time != old_time) {
            team.recompute_visible(problem_count);
        }
    }

    void freeze_scoreboard() {
        if (frozen) {
            cout << "[Error]Freeze failed: scoreboard has been frozen.\n";
            return;
        }
        frozen = true;
        cout << "[Info]Freeze scoreboard.\n";
    }

    void flush_command() {
        flush_scoreboard();
        cout << "[Info]Flush scoreboard.\n";
    }

    void reveal_problem(int team_idx, int problem_idx) {
        Team& team = teams[team_idx];
        ProblemState& problem = team.problems[problem_idx];
        if (!problem.frozen) {
            return;
        }
        problem.visible_wrong = problem.final_wrong;
        problem.visible_solved = problem.final_solved;
        problem.visible_ac_time = problem.final_ac_time;
        problem.frozen = false;
        problem.frozen_post_count = 0;
        --team.frozen_problem_count;
        team.recompute_visible(problem_count);
    }

    void scroll_scoreboard() {
        if (!frozen) {
            cout << "[Error]Scroll failed: scoreboard has not been frozen.\n";
            return;
        }
        cout << "[Info]Scroll scoreboard.\n";
        flush_scoreboard();
        print_scoreboard();

        RankTree ranking_tree;
        RankTree frozen_tree;
        for (int i = 0; i < static_cast<int>(teams.size()); ++i) {
            ranking_tree.insert(i);
            if (teams[i].frozen_problem_count > 0) {
                frozen_tree.insert(i);
            }
        }

        while (!frozen_tree.empty()) {
            int team_idx = *frozen_tree.find_by_order(static_cast<int>(frozen_tree.size()) - 1);
            int problem_idx = -1;
            for (int i = 0; i < problem_count; ++i) {
                if (teams[team_idx].problems[i].frozen) {
                    problem_idx = i;
                    break;
                }
            }

            int old_pos = static_cast<int>(ranking_tree.order_of_key(team_idx));
            ranking_tree.erase(team_idx);
            frozen_tree.erase(team_idx);

            reveal_problem(team_idx, problem_idx);

            ranking_tree.insert(team_idx);
            if (teams[team_idx].frozen_problem_count > 0) {
                frozen_tree.insert(team_idx);
            }

            int new_pos = static_cast<int>(ranking_tree.order_of_key(team_idx));
            if (new_pos < old_pos && new_pos + 1 < static_cast<int>(ranking_tree.size())) {
                int replaced_team = *ranking_tree.find_by_order(new_pos + 1);
                cout << teams[team_idx].name << ' ' << teams[replaced_team].name << ' '
                     << teams[team_idx].visible_solved << ' ' << teams[team_idx].visible_penalty << '\n';
            }
        }

        vector<int> ids;
        ids.reserve(teams.size());
        for (auto it = ranking_tree.begin(); it != ranking_tree.end(); ++it) {
            ids.push_back(*it);
        }
        rebuild_ranking_cache_from_sorted_ids(ids);
        frozen = false;
        has_flushed = true;
        print_scoreboard();
    }

    void query_ranking(const string& name) const {
        auto it = team_id.find(name);
        if (it == team_id.end()) {
            cout << "[Error]Query ranking failed: cannot find the team.\n";
            return;
        }
        cout << "[Info]Complete query ranking.\n";
        if (frozen) {
            cout << "[Warning]Scoreboard is frozen. The ranking may be inaccurate until it were scrolled.\n";
        }
        int id = it->second;
        int rank = (!has_flushed || ranking_of_team.empty()) ? name_rank_before_first_flush.at(name)
                                                             : ranking_of_team[id];
        cout << name << " NOW AT RANKING " << rank << '\n';
    }

    void query_submission(const string& name, char problem_name, const string& status) const {
        auto it = team_id.find(name);
        if (it == team_id.end()) {
            cout << "[Error]Query submission failed: cannot find the team.\n";
            return;
        }
        cout << "[Info]Complete query submission.\n";
        int id = it->second;
        int time = teams[id].latest_submission[problem_name - 'A'][status_index(status)];
        if (time == 0) {
            cout << "Cannot find any submission.\n";
            return;
        }
        cout << name << ' ' << problem_name << ' ' << status << ' ' << time << '\n';
    }
};

bool RankCompare::operator()(int lhs, int rhs) const {
    return g_contest->better_team(lhs, rhs);
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    Contest contest;
    string line;
    while (getline(cin, line)) {
        if (line.empty()) {
            continue;
        }
        istringstream iss(line);
        string command;
        iss >> command;

        if (command == "ADDTEAM") {
            string team_name;
            iss >> team_name;
            contest.add_team(team_name);
            continue;
        }

        if (command == "START") {
            string duration_word;
            int duration_time;
            string problem_word;
            int problems;
            iss >> duration_word >> duration_time >> problem_word >> problems;
            contest.start_contest(problems);
            continue;
        }

        if (command == "SUBMIT") {
            char problem_name;
            string by_word;
            string team_name;
            string with_word;
            string status;
            string at_word;
            int time;
            iss >> problem_name >> by_word >> team_name >> with_word >> status >> at_word >> time;
            contest.submit(problem_name, team_name, status, time);
            continue;
        }

        if (command == "FLUSH") {
            contest.flush_command();
            continue;
        }

        if (command == "FREEZE") {
            contest.freeze_scoreboard();
            continue;
        }

        if (command == "SCROLL") {
            contest.scroll_scoreboard();
            continue;
        }

        if (command == "QUERY_RANKING") {
            string team_name;
            iss >> team_name;
            contest.query_ranking(team_name);
            continue;
        }

        if (command == "QUERY_SUBMISSION") {
            string team_name;
            string where_word;
            string problem_token;
            string and_word;
            string status_token;
            iss >> team_name >> where_word >> problem_token >> and_word >> status_token;
            char problem_name = problem_token.back();
            string status = status_token.substr(status_token.find('=') + 1);
            contest.query_submission(team_name, problem_name, status);
            continue;
        }

        if (command == "END") {
            cout << "[Info]Competition ends.\n";
            break;
        }
    }

    return 0;
}
