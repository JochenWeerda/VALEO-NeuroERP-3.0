# CI-Evidenz: Grenzen und Wiederverwendung

Lesender Audit: verify_quality_evidence.py bindet Coverage-Dateibytes an denselben Commit, nicht an einen vollstaendigen Quell-/Toolchain-Hash. Ein frueh hochgeladenes Coverage-Artefakt allein bestaetigt keinen erfolgreichen Frontendjob. Der aktuelle Sonar-Weg wartet im selben Run ueber Jobabhaengigkeiten auf Erfolg.

Laufuebergreifende Wiederverwendung ist noch nicht implementiert oder freigegeben. Voraussetzung: konservativer Inputhash inklusive Quellpaketen, Lock/Workspace/Build-/Tests, Schemas/Generatorinputs, Workflow/Actions und Toolchain; unabhaengig verifizierter erfolgreicher Herkunftslauf aus vertrauenswuerdigem Repo/Workflow/Branch beziehungsweise PR; Bytepruefung und unveraenderte Herkunfts-SHA. Keine fremden Fork-Artefakte oder alleinige Manifestbehauptungen. Coverage erst nach ganzem erfolgreichen Kern bereitstellen; Sonar am aktuellen Commit mit unveraenderten Schwellen beibehalten.

Bei fehlenden, externen oder unklaren Inputs, falscher Herkunft, erfolglosem Build oder manipulierten Bytes regulaer testen. Negativtests muessen diese Faelle sowie geaenderte Locks/Schemas/Workflow erkennen. Reine Doc-Aenderungen duerfen den Kern erst nach diesen Nachweisen wiederverwenden. Der Integrationslauf 42410114687 wird fuer diesen Audit nicht veraendert.
