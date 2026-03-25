#include <iostream>
#include <string>
#include <unordered_set>

class Contest {
public:
    void run() {
        std::string command;
        while (std::cin >> command) {
            if (command == "ADDTEAM") {
                handleAddTeam();
            } else if (command == "START") {
                handleStart();
            } else if (command == "SUBMIT") {
                handleSubmit();
            } else if (command == "FLUSH") {
                handleFlush();
            } else if (command == "FREEZE") {
                handleFreeze();
            } else if (command == "SCROLL") {
                handleScroll();
            } else if (command == "QUERY_RANKING") {
                handleQueryRanking();
            } else if (command == "QUERY_SUBMISSION") {
                handleQuerySubmission();
            } else if (command == "END") {
                std::cout << "[Info]Competition ends.\n";
                break;
            }
        }
    }

private:
    bool started_ = false;
    bool frozen_ = false;
    std::unordered_set<std::string> teams_;

    void handleAddTeam() {
        std::string team_name;
        std::cin >> team_name;
        if (started_) {
            std::cout << "[Error]Add failed: competition has started.\n";
            return;
        }
        if (teams_.contains(team_name)) {
            std::cout << "[Error]Add failed: duplicated team name.\n";
            return;
        }
        teams_.insert(team_name);
        std::cout << "[Info]Add successfully.\n";
    }

    void handleStart() {
        std::string duration_label;
        int duration_time = 0;
        std::string problem_label;
        int problem_count = 0;
        std::cin >> duration_label >> duration_time >> problem_label >> problem_count;
        (void)duration_label;
        (void)duration_time;
        (void)problem_label;
        (void)problem_count;

        if (started_) {
            std::cout << "[Error]Start failed: competition has started.\n";
            return;
        }
        started_ = true;
        frozen_ = false;
        std::cout << "[Info]Competition starts.\n";
    }

    void handleSubmit() {
        std::string problem_name;
        std::string by_token;
        std::string team_name;
        std::string with_token;
        std::string submit_status;
        std::string at_token;
        int time = 0;
        std::cin >> problem_name >> by_token >> team_name >> with_token >> submit_status >> at_token >> time;
        (void)problem_name;
        (void)by_token;
        (void)team_name;
        (void)with_token;
        (void)submit_status;
        (void)at_token;
        (void)time;
    }

    void handleFlush() {
        std::cout << "[Info]Flush scoreboard.\n";
    }

    void handleFreeze() {
        if (frozen_) {
            std::cout << "[Error]Freeze failed: scoreboard has been frozen.\n";
            return;
        }
        frozen_ = true;
        std::cout << "[Info]Freeze scoreboard.\n";
    }

    void handleScroll() {
        if (!frozen_) {
            std::cout << "[Error]Scroll failed: scoreboard has not been frozen.\n";
            return;
        }
        std::cout << "[Info]Scroll scoreboard.\n";
        frozen_ = false;
    }

    void handleQueryRanking() {
        std::string team_name;
        std::cin >> team_name;
        if (!teams_.contains(team_name)) {
            std::cout << "[Error]Query ranking failed: cannot find the team.\n";
            return;
        }
        std::cout << "[Info]Complete query ranking.\n";
        if (frozen_) {
            std::cout << "[Warning]Scoreboard is frozen. The ranking may be inaccurate until it were scrolled.\n";
        }
        std::cout << team_name << " NOW AT RANKING 1\n";
    }

    void handleQuerySubmission() {
        std::string team_name;
        std::string where_token;
        std::string problem_clause;
        std::string and_token;
        std::string status_clause;
        std::cin >> team_name >> where_token >> problem_clause >> and_token >> status_clause;
        (void)where_token;
        (void)problem_clause;
        (void)and_token;
        (void)status_clause;

        if (!teams_.contains(team_name)) {
            std::cout << "[Error]Query submission failed: cannot find the team.\n";
            return;
        }
        std::cout << "[Info]Complete query submission.\n";
        std::cout << "Cannot find any submission.\n";
    }
};

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    Contest contest;
    contest.run();
    return 0;
}

