"use strict";
/**
 * FinanzDebitor domain entity generated from CRM migration toolkit.
 * Keep the structure focused on pure data/behavior, no infrastructure here.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.FinanzDebitor = void 0;
class FinanzDebitor {
    constructor(props) {
        this.props = props;
    }
    static create(props) {
        return new FinanzDebitor(props);
    }
    get id() {
        return this.props.id;
    }
    get kundenId() {
        return this.props.kunden_id;
    }
    get debitorNr() {
        return this.props.debitor_nr;
    }
    get kreditlimit() {
        return this.props.kreditlimit;
    }
    get zahlungsziel() {
        return this.props.zahlungsziel;
    }
    get zahlungsart() {
        return this.props.zahlungsart;
    }
    get bankverbindung() {
        return this.props.bankverbindung;
    }
    get steuernummer() {
        return this.props.steuernummer;
    }
    get ustId() {
        return this.props.ust_id;
    }
    get istAktiv() {
        return this.props.ist_aktiv;
    }
    get notizen() {
        return this.props.notizen;
    }
    get erstelltVon() {
        return this.props.erstellt_von;
    }
    get erstelltAm() {
        return this.props.erstellt_am;
    }
    get aktualisiertAm() {
        return this.props.aktualisiert_am;
    }
    toPrimitives() {
        return { ...this.props };
    }
}
exports.FinanzDebitor = FinanzDebitor;
//# sourceMappingURL=finanzDebitor.entity.js.map