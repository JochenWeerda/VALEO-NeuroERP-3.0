"use strict";
/**
 * FinanzKonto domain entity generated from CRM migration toolkit.
 * Keep the structure focused on pure data/behavior, no infrastructure here.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.FinanzKonto = void 0;
class FinanzKonto {
    constructor(props) {
        this.props = props;
    }
    static create(props) {
        return new FinanzKonto(props);
    }
    get id() {
        return this.props.id;
    }
    get kontonummer() {
        return this.props.kontonummer;
    }
    get kontobezeichnung() {
        return this.props.kontobezeichnung;
    }
    get kontotyp() {
        return this.props.kontotyp;
    }
    get kontenklasse() {
        return this.props.kontenklasse;
    }
    get kontengruppe() {
        return this.props.kontengruppe;
    }
    get istAktiv() {
        return this.props.ist_aktiv;
    }
    get istSteuerpflichtig() {
        return this.props.ist_steuerpflichtig;
    }
    get steuersatz() {
        return this.props.steuersatz;
    }
    get beschreibung() {
        return this.props.beschreibung;
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
exports.FinanzKonto = FinanzKonto;
//# sourceMappingURL=finanzKonto.entity.js.map