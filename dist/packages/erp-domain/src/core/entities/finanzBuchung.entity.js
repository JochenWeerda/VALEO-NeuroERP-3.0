"use strict";
/**
 * FinanzBuchung domain entity generated from CRM migration toolkit.
 * Keep the structure focused on pure data/behavior, no infrastructure here.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.FinanzBuchung = void 0;
class FinanzBuchung {
    props;
    constructor(props) {
        this.props = props;
    }
    static create(props) {
        return new FinanzBuchung(props);
    }
    get id() {
        return this.props.id;
    }
    get buchungsnummer() {
        return this.props.buchungsnummer;
    }
    get buchungsdatum() {
        return this.props.buchungsdatum;
    }
    get belegdatum() {
        return this.props.belegdatum;
    }
    get belegnummer() {
        return this.props.belegnummer;
    }
    get buchungstext() {
        return this.props.buchungstext;
    }
    get sollkonto() {
        return this.props.sollkonto;
    }
    get habenkonto() {
        return this.props.habenkonto;
    }
    get betrag() {
        return this.props.betrag;
    }
    get waehrung() {
        return this.props.waehrung;
    }
    get steuerbetrag() {
        return this.props.steuerbetrag;
    }
    get steuersatz() {
        return this.props.steuersatz;
    }
    get buchungsart() {
        return this.props.buchungsart;
    }
    get referenzTyp() {
        return this.props.referenz_typ;
    }
    get referenzId() {
        return this.props.referenz_id;
    }
    get istStorniert() {
        return this.props.ist_storniert;
    }
    get stornoBuchungId() {
        return this.props.storno_buchung_id;
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
exports.FinanzBuchung = FinanzBuchung;
