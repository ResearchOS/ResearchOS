# Roadmap

## Version 0.1

- [x] Do multiple things with one Action.
- [x] Create research objects, save and load them with attributes
- [x] Create edges between research objects and allow the edges to have their own attributes.
- [x] Load and save even complex attributes (e.g. list of dicts) with JSON. Right now I'm just using json.loads()/dumps() but I may need something more sophisticated.
- [x] Implement Logsheet
    - [x] Implement read logsheet.
        - [x] Populate the database with the logsheet data.
- [x] Implement saving participant data to disk/the database.
    - [x] Implement data schema for participant data
- [x] Implement subsets.
- [~] Publish my proof of concept to JOSS.

## Version 0.2
- [x] Implement Plots
- [ ] Implement Stats
- [ ] Create a graph of research objects and edges
- [ ] Implement rollback-able version history for research objects
- [ ] Enhance multi-user support on the same machine.
- [ ] Look into CI/CD best practices, improve test coverage.
- [ ] Import/export a ResearchObject for sharing with other users (using Parquet or something similar).
- [ ] Allow exporting stats results to LaTeX table templates (e.g. fill in ? with values).
- [ ] Export data to a CSV file in the common statistical format for processing in other software.

## Version 0.3 and beyond
- [ ] Implement a MariaDB-based backend for ResearchOS so that it can be used in a multi-user environment.
- [ ] Implement password-based authentication for the MariaDB backend.
- [ ] Implement a web-based frontend for ResearchOS.
- [ ] Get journals on board with ResearchOS so that they can accept ResearchObjects with submissions.
- [ ] Integrate ResearchOS with participant management systems like RedHat so that participants & data are linked.